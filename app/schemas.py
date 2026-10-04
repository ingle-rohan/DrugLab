"""DrugLab / DrugPedia - Pydantic v2 request / response schemas (Phase 1).

Conventions
-----------
* ``*Base``   - fields shared by create and read.
* ``*Create`` - request payload (no ids, no timestamps, no tenant_id: the
                tenant is always taken from the authenticated context).
* ``*Update`` - partial update (PATCH).
* ``*Read``   - response, always carries provenance (source + evidence level).
"""

import re
import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Annotated, Generic, Optional, TypeVar

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    StringConstraints,
    computed_field,
    field_validator,
    model_validator,
)

from .models import (
    COMPATIBILITY_CATEGORY_CODE,
    AccessDepth,
    BCSClass,
    BrandVerificationStatus,
    CompatibilityCategory,
    ConfidenceLevel,
    EvidenceLevel,
    FormTag,
    IdentifierType,
    MetricType,
    RecordStatus,
    SourceType,
    UserRole,
    ValueOrigin,
)

# --------------------------------------------------------------------------
# Shared types & validators
# --------------------------------------------------------------------------
EVIDENCE_LABELS: dict[EvidenceLevel, str] = {
    EvidenceLevel.A: "Regulatory / official / pharmacopoeial",
    EvidenceLevel.B: "Peer-reviewed primary research",
    EvidenceLevel.C: "Authoritative scientific database",
    EvidenceLevel.D: "Secondary source",
    EvidenceLevel.E: "Limited evidence / commercial listing",
}

INCHIKEY_RE = re.compile(r"^[A-Z]{14}-[A-Z]{10}-[A-Z]$")
CAS_RE = re.compile(r"^[0-9]{2,7}-[0-9]{2}-[0-9]$")
ATC_RE = re.compile(r"^[A-Z][0-9]{2}[A-Z]{2}[0-9]{2}$")
PMID_RE = re.compile(r"^[0-9]{1,9}$")
DOI_RE = re.compile(r"^10\.\d{4,9}/\S+$")

DIMENSIONLESS_METRICS = {
    MetricType.PKA,
    MetricType.LOGP,
    MetricType.LOGD,
    MetricType.XLOGP3,
    MetricType.HBD,
    MetricType.HBA,
    MetricType.ROTATABLE_BONDS,
}

NonEmptyStr = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
Name255 = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=255)]


def cas_checksum_ok(cas: str) -> bool:
    """CAS Registry Number check digit (e.g. 15687-27-1 is valid)."""
    if not CAS_RE.match(cas):
        return False
    digits = cas.replace("-", "")
    body, check = digits[:-1], int(digits[-1])
    total = sum(int(d) * i for i, d in enumerate(reversed(body), start=1))
    return total % 10 == check


def _validate_cas(v: Optional[str]) -> Optional[str]:
    if v is None:
        return v
    if not cas_checksum_ok(v):
        raise ValueError(f"'{v}' is not a valid CAS Registry Number (format or check digit)")
    return v


def _validate_pmid(v: Optional[str]) -> Optional[str]:
    if v is not None and not PMID_RE.match(v):
        raise ValueError("PMID must be 1-9 digits")
    return v


def _validate_doi(v: Optional[str]) -> Optional[str]:
    if v is not None and not DOI_RE.match(v):
        raise ValueError("DOI must look like 10.xxxx/...")
    return v


class APIModel(BaseModel):
    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True, extra="forbid")


class ReadModel(BaseModel):
    """Read models tolerate extra ORM attributes and never strip on output."""

    model_config = ConfigDict(from_attributes=True)


T = TypeVar("T")


class PageParams(APIModel):
    offset: int = Field(0, ge=0)
    limit: int = Field(25, ge=1, le=200)


class Page(ReadModel, Generic[T]):
    items: list[T]
    total: int
    offset: int
    limit: int


# --------------------------------------------------------------------------
# Provenance
# --------------------------------------------------------------------------
class SourceBase(APIModel):
    name: Annotated[str, StringConstraints(min_length=1, max_length=500)]
    document_title: Optional[str] = None
    url: Optional[Annotated[str, StringConstraints(pattern=r"^https?://\S+$")]] = None
    source_type: SourceType
    default_evidence_level: EvidenceLevel
    version_or_edition: Optional[str] = Field(None, max_length=255)
    record_id: Optional[str] = Field(None, max_length=255)
    doi: Optional[str] = None
    pmid: Optional[str] = None
    publication_date: Optional[date] = None
    access_date: Optional[date] = None
    access_depth: AccessDepth = AccessDepth.NOT_OPENED
    licence_status: Optional[str] = None
    is_mirror_or_aggregator: bool = False
    notes: Optional[str] = None

    _v_doi = field_validator("doi")(_validate_doi)
    _v_pmid = field_validator("pmid")(_validate_pmid)

    @model_validator(mode="after")
    def _level_matches_type(self) -> "SourceBase":
        """A commercial listing or mirror can never be level A/B."""
        if self.source_type in {SourceType.COMMERCIAL_LISTING, SourceType.REPOSITORY_OR_THESIS} or self.is_mirror_or_aggregator:
            if self.default_evidence_level in {EvidenceLevel.A, EvidenceLevel.B}:
                raise ValueError("commercial listings, repositories and mirrors cannot be evidence level A or B")
        if self.source_type in {SourceType.REGULATORY_LABEL, SourceType.REGULATORY_COMMUNICATION,
                                SourceType.PHARMACOPOEIAL, SourceType.GOVERNMENT_LIST}:
            if self.default_evidence_level != EvidenceLevel.A:
                raise ValueError("regulatory / pharmacopoeial / government sources must be evidence level A")
        return self


class SourceCreate(SourceBase):
    pass


class SourceRead(SourceBase, ReadModel):
    model_config = ConfigDict(from_attributes=True, extra="ignore")
    id: uuid.UUID
    tenant_id: Optional[uuid.UUID] = None
    created_at: datetime
    updated_at: datetime


class SourceBrief(ReadModel):
    id: uuid.UUID
    name: str
    url: Optional[str] = None
    doi: Optional[str] = None
    pmid: Optional[str] = None
    source_type: SourceType
    publication_date: Optional[date] = None
    access_date: Optional[date] = None
    access_depth: AccessDepth


class ProvenanceCreate(APIModel):
    source_id: uuid.UUID
    evidence_level: EvidenceLevel
    source_locator: Optional[str] = Field(None, max_length=255, description="e.g. 'DailyMed 12.3 Table 11'")
    source_date: Optional[date] = None


class ProvenanceRead(ReadModel):
    source_id: uuid.UUID
    evidence_level: EvidenceLevel
    source_locator: Optional[str] = None
    source_date: Optional[date] = None
    source: SourceBrief

    @computed_field  # type: ignore[prop-decorator]
    @property
    def evidence_label(self) -> str:
        return EVIDENCE_LABELS[self.evidence_level]


# --------------------------------------------------------------------------
# Tenancy
# --------------------------------------------------------------------------
class TenantCreate(APIModel):
    name: Name255
    slug: Annotated[str, StringConstraints(pattern=r"^[a-z0-9][a-z0-9-]{1,62}$")]
    plan: Annotated[str, StringConstraints(pattern=r"^(free|professional|enterprise)$")] = "free"


class TenantRead(ReadModel):
    id: uuid.UUID
    name: str
    slug: str
    plan: str
    is_active: bool
    created_at: datetime


class UserCreate(APIModel):
    email: EmailStr
    full_name: Name255
    password: Annotated[str, StringConstraints(min_length=12, max_length=128)]
    role: UserRole = UserRole.VIEWER

    @field_validator("role")
    @classmethod
    def _no_platform_admin_via_api(cls, v: UserRole) -> UserRole:
        if v == UserRole.PLATFORM_ADMIN:
            raise ValueError("platform_admin cannot be assigned through the public API")
        return v


class UserRead(ReadModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    email: EmailStr
    full_name: str
    role: UserRole
    is_active: bool
    created_at: datetime


# --------------------------------------------------------------------------
# Drug identifiers & drug
# --------------------------------------------------------------------------
class DrugIdentifierCreate(ProvenanceCreate):
    id_type: IdentifierType
    value: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=128)]
    applies_to_form: Optional[FormTag] = None
    note: Optional[str] = None

    @model_validator(mode="after")
    def _check_value(self) -> "DrugIdentifierCreate":
        if self.id_type == IdentifierType.CAS:
            _validate_cas(self.value)
        elif self.id_type == IdentifierType.ATC and not ATC_RE.match(self.value):
            raise ValueError("ATC code must look like M01AE01")
        elif self.id_type == IdentifierType.PUBCHEM_CID and not self.value.isdigit():
            raise ValueError("PubChem CID must be numeric")
        elif self.id_type == IdentifierType.UNII and not re.fullmatch(r"[A-Z0-9]{10}", self.value):
            raise ValueError("UNII must be 10 upper-case alphanumeric characters")
        return self


class DrugIdentifierRead(ProvenanceRead):
    id: uuid.UUID
    drug_id: uuid.UUID
    id_type: IdentifierType
    value: str
    applies_to_form: Optional[FormTag] = None
    note: Optional[str] = None


class DrugBase(APIModel):
    generic_name: Name255
    form_tag: FormTag = FormTag.PARENT
    form_description: Optional[str] = Field(None, max_length=255)
    inn: Optional[str] = Field(None, max_length=255)
    usan: Optional[str] = Field(None, max_length=255)
    ban: Optional[str] = Field(None, max_length=255)
    us_name: Optional[str] = Field(None, max_length=255)
    synonyms: list[str] = Field(default_factory=list)
    therapeutic_class: Optional[str] = Field(None, max_length=255)
    pharmacological_class: Optional[str] = Field(None, max_length=255)
    chemical_class: Optional[str] = Field(None, max_length=255)
    atc_code: Optional[str] = None
    cas_number: Optional[str] = None
    unii: Optional[Annotated[str, StringConstraints(pattern=r"^[A-Z0-9]{10}$")]] = None
    pubchem_cid: Optional[int] = Field(None, gt=0)
    active_moiety: Optional[str] = Field(None, max_length=255)
    is_prodrug: Optional[bool] = None

    iupac_name: Optional[str] = None
    molecular_formula: Optional[Annotated[str, StringConstraints(pattern=r"^[A-Za-z0-9·.()]+$", max_length=128)]] = None
    molecular_weight: Optional[Decimal] = Field(None, gt=0, max_digits=10, decimal_places=3)
    exact_mass: Optional[Decimal] = Field(None, gt=0, max_digits=14, decimal_places=9)
    smiles_isomeric: Optional[str] = None
    smiles_canonical: Optional[str] = None
    inchi: Optional[Annotated[str, StringConstraints(pattern=r"^InChI=1S?/\S+$")]] = None
    inchikey: Optional[str] = None
    stereocentre_count: Optional[int] = Field(None, ge=0, le=200)
    stereochemistry_note: Optional[str] = None
    functional_groups: list[str] = Field(default_factory=list)

    mechanism_of_action: Optional[str] = None
    pharmacological_action: Optional[str] = None
    scope_note: Optional[str] = None

    @field_validator("cas_number")
    @classmethod
    def _cas(cls, v: Optional[str]) -> Optional[str]:
        return _validate_cas(v)

    @field_validator("atc_code")
    @classmethod
    def _atc(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not ATC_RE.match(v):
            raise ValueError("ATC code must look like J01FA10")
        return v

    @field_validator("inchikey")
    @classmethod
    def _inchikey(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not INCHIKEY_RE.match(v):
            raise ValueError("InChIKey must match XXXXXXXXXXXXXX-XXXXXXXXXX-X")
        return v

    @model_validator(mode="after")
    def _structure_consistency(self) -> "DrugBase":
        # InChIKey 2nd block 'UHFFFAOYSA' means "no stereo": it must not coexist with defined stereocentres.
        if self.inchikey and self.stereocentre_count:
            if self.inchikey.split("-")[1].endswith("UHFFFAOYSA") and self.stereocentre_count > 0:
                if self.smiles_isomeric and "@" in self.smiles_isomeric:
                    raise ValueError("InChIKey has no stereo layer but isomeric SMILES contains stereo marks")
        # InChI formula layer must match molecular_formula when both are given (anhydrous basis).
        if self.inchi and self.molecular_formula and self.form_tag in {FormTag.PARENT, FormTag.ANHYDROUS}:
            parts = self.inchi.split("/")
            if len(parts) > 1 and parts[1] != self.molecular_formula:
                raise ValueError(
                    f"InChI formula layer '{parts[1]}' does not match molecular_formula '{self.molecular_formula}'"
                )
        return self


class DrugCreate(DrugBase):
    identity_source_id: Optional[uuid.UUID] = None
    identity_evidence_level: Optional[EvidenceLevel] = None
    date_researched: Optional[date] = None
    identifiers: list[DrugIdentifierCreate] = Field(default_factory=list)

    @model_validator(mode="after")
    def _identity_needs_source(self) -> "DrugCreate":
        if (self.identity_source_id is None) != (self.identity_evidence_level is None):
            raise ValueError("identity_source_id and identity_evidence_level must be provided together")
        return self


class DrugUpdate(APIModel):
    """PATCH payload. record_status transitions go through the dedicated verify endpoint."""

    generic_name: Optional[Name255] = None
    form_description: Optional[str] = None
    inn: Optional[str] = None
    usan: Optional[str] = None
    ban: Optional[str] = None
    us_name: Optional[str] = None
    synonyms: Optional[list[str]] = None
    therapeutic_class: Optional[str] = None
    pharmacological_class: Optional[str] = None
    chemical_class: Optional[str] = None
    atc_code: Optional[str] = None
    cas_number: Optional[str] = None
    unii: Optional[Annotated[str, StringConstraints(pattern=r"^[A-Z0-9]{10}$")]] = None
    pubchem_cid: Optional[int] = Field(None, gt=0)
    iupac_name: Optional[str] = None
    molecular_formula: Optional[str] = None
    molecular_weight: Optional[Decimal] = Field(None, gt=0, max_digits=10, decimal_places=3)
    exact_mass: Optional[Decimal] = Field(None, gt=0, max_digits=14, decimal_places=9)
    smiles_isomeric: Optional[str] = None
    smiles_canonical: Optional[str] = None
    inchi: Optional[str] = None
    inchikey: Optional[str] = None
    mechanism_of_action: Optional[str] = None
    pharmacological_action: Optional[str] = None
    scope_note: Optional[str] = None

    _v_cas = field_validator("cas_number")(_validate_cas)

    @field_validator("inchikey")
    @classmethod
    def _inchikey(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not INCHIKEY_RE.match(v):
            raise ValueError("InChIKey must match XXXXXXXXXXXXXX-XXXXXXXXXX-X")
        return v


class DrugVerifyRequest(APIModel):
    """Human verification gate: draft -> partially_verified -> human_verified -> published."""

    target_status: RecordStatus
    verified_on: date = Field(default_factory=date.today)

    @field_validator("target_status")
    @classmethod
    def _not_draft(cls, v: RecordStatus) -> RecordStatus:
        if v == RecordStatus.DRAFT:
            raise ValueError("cannot move a record back to draft through the verify endpoint")
        return v


class DrugSummary(ReadModel):
    id: uuid.UUID
    generic_name: str
    form_tag: FormTag
    inn: Optional[str] = None
    therapeutic_class: Optional[str] = None
    atc_code: Optional[str] = None
    cas_number: Optional[str] = None
    molecular_formula: Optional[str] = None
    molecular_weight: Optional[Decimal] = None
    record_status: RecordStatus
    identity_evidence_level: Optional[EvidenceLevel] = None


class DrugRead(DrugBase, ReadModel):
    model_config = ConfigDict(from_attributes=True, extra="ignore")
    id: uuid.UUID
    tenant_id: Optional[uuid.UUID] = None
    record_status: RecordStatus
    date_researched: Optional[date] = None
    date_last_verified: Optional[date] = None
    verified_by_user_id: Optional[uuid.UUID] = None
    verified_at: Optional[datetime] = None
    identity_source: Optional[SourceBrief] = None
    identity_evidence_level: Optional[EvidenceLevel] = None
    open_conflict_count: int = 0
    created_at: datetime
    updated_at: datetime


# --------------------------------------------------------------------------
# Preformulation metrics & BCS
# --------------------------------------------------------------------------
class PreformulationMetricBase(APIModel):
    metric_type: MetricType
    metric_label: Optional[str] = Field(None, max_length=128)
    value_numeric: Optional[Decimal] = None
    value_min: Optional[Decimal] = None
    value_max: Optional[Decimal] = None
    value_text: Optional[str] = None
    unit: Optional[str] = Field(None, max_length=32)
    origin: ValueOrigin
    temperature_c: Optional[Decimal] = Field(None, ge=-273.15, le=1000)
    ph: Optional[Decimal] = Field(None, ge=0, le=14)
    ionic_strength: Optional[Decimal] = Field(None, ge=0)
    medium: Optional[str] = Field(None, max_length=255)
    method: Optional[str] = Field(None, max_length=255)
    solid_form: Optional[str] = Field(None, max_length=64)
    ionizable_group: Optional[str] = Field(None, max_length=32)
    pka_ordinal: Optional[int] = Field(None, ge=1, le=5)
    conflict_flag: bool = False
    notes: Optional[str] = None

    @model_validator(mode="after")
    def _check_value_and_unit(self) -> "PreformulationMetricBase":
        has_number = any(x is not None for x in (self.value_numeric, self.value_min, self.value_max))
        if not has_number and not self.value_text:
            raise ValueError("provide value_numeric, a value_min/value_max range, or value_text")
        if self.value_numeric is not None and (self.value_min is not None or self.value_max is not None):
            raise ValueError("use either value_numeric or value_min/value_max, not both")
        if self.value_min is not None and self.value_max is not None and self.value_min > self.value_max:
            raise ValueError("value_min must be <= value_max")
        if has_number and self.metric_type not in DIMENSIONLESS_METRICS and not self.unit:
            raise ValueError(f"unit is required for numeric {self.metric_type.value} values")
        if self.metric_type == MetricType.OTHER and not self.metric_label:
            raise ValueError("metric_label is required when metric_type is 'other'")
        if self.metric_type == MetricType.PKA:
            for v in (self.value_numeric, self.value_min, self.value_max):
                if v is not None and not (Decimal("-5") <= v <= Decimal("25")):
                    raise ValueError("pKa outside plausible range -5..25")
        if self.metric_type in {MetricType.XLOGP3, MetricType.TPSA, MetricType.HBD, MetricType.HBA,
                                MetricType.ROTATABLE_BONDS} and self.origin not in {ValueOrigin.COMPUTED, ValueOrigin.PREDICTED}:
            raise ValueError(f"{self.metric_type.value} is a computed descriptor; origin must be computed/predicted")
        if self.metric_type == MetricType.PH_SOLUBILITY and self.ph is None:
            raise ValueError("pH-dependent solubility requires ph")
        return self


class PreformulationMetricCreate(PreformulationMetricBase, ProvenanceCreate):
    drug_id: uuid.UUID
    conflict_id: Optional[uuid.UUID] = None

    @model_validator(mode="after")
    def _conflict_consistency(self) -> "PreformulationMetricCreate":
        if self.conflict_id is not None and not self.conflict_flag:
            raise ValueError("conflict_flag must be true when conflict_id is set")
        return self


class PreformulationMetricRead(PreformulationMetricBase, ProvenanceRead):
    model_config = ConfigDict(from_attributes=True, extra="ignore")
    id: uuid.UUID
    drug_id: uuid.UUID
    conflict_id: Optional[uuid.UUID] = None
    created_at: datetime


class BCSAssessmentBase(APIModel):
    bcs_class: Optional[BCSClass] = None
    framework: Optional[str] = Field(None, max_length=255)
    dose_mg_min: Optional[Decimal] = Field(None, ge=0)
    dose_mg_max: Optional[Decimal] = Field(None, ge=0)
    solubility_basis: Optional[str] = None
    permeability_basis: Optional[str] = None
    is_disputed: bool = False
    is_regulatory_classification: bool = False
    rationale: Optional[str] = None

    @model_validator(mode="after")
    def _check(self) -> "BCSAssessmentBase":
        if self.dose_mg_min is not None and self.dose_mg_max is not None and self.dose_mg_min > self.dose_mg_max:
            raise ValueError("dose_mg_min must be <= dose_mg_max")
        if self.bcs_class is None and not self.is_disputed:
            raise ValueError("bcs_class may only be empty when the classification is flagged as disputed")
        return self


class BCSAssessmentCreate(BCSAssessmentBase, ProvenanceCreate):
    drug_id: uuid.UUID
    conflict_id: Optional[uuid.UUID] = None


class BCSAssessmentRead(BCSAssessmentBase, ProvenanceRead):
    model_config = ConfigDict(from_attributes=True, extra="ignore")
    id: uuid.UUID
    drug_id: uuid.UUID
    conflict_id: Optional[uuid.UUID] = None


# --------------------------------------------------------------------------
# Dose tracking
# --------------------------------------------------------------------------
class DoseGuidelineBase(APIModel):
    population: Name255
    route: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=32)]
    indication: Optional[str] = Field(None, max_length=255)
    regimen_text: NonEmptyStr
    dose_mg_min: Optional[Decimal] = Field(None, ge=0)
    dose_mg_max: Optional[Decimal] = Field(None, ge=0)
    dose_mg_per_kg_min: Optional[Decimal] = Field(None, ge=0)
    dose_mg_per_kg_max: Optional[Decimal] = Field(None, ge=0)
    per_kg_basis: Optional[Annotated[str, StringConstraints(pattern=r"^(per_dose|per_day)$")]] = None
    interval_hours: Optional[Decimal] = Field(None, gt=0)
    duration_days: Optional[Decimal] = Field(None, gt=0)
    max_daily_dose_mg: Optional[Decimal] = Field(None, gt=0)
    max_daily_dose_period_hours: Optional[int] = Field(24, gt=0, le=168)
    weight_min_kg: Optional[Decimal] = Field(None, ge=0)
    weight_max_kg: Optional[Decimal] = Field(None, ge=0)
    gfr_min_ml_min: Optional[Decimal] = Field(None, ge=0)
    gfr_max_ml_min: Optional[Decimal] = Field(None, ge=0)
    jurisdiction: Annotated[str, StringConstraints(pattern=r"^(US|UK|EU|IN|CA|WHO|OTHER)$")]
    product_context: Optional[str] = Field(None, max_length=255)
    label_revision_date: Optional[date] = None
    is_current_label: bool = True
    is_product_specific: bool = True
    safety_critical: bool = True
    requires_human_verification: bool = True

    @model_validator(mode="after")
    def _check(self) -> "DoseGuidelineBase":
        pairs = [
            (self.dose_mg_min, self.dose_mg_max, "dose_mg"),
            (self.dose_mg_per_kg_min, self.dose_mg_per_kg_max, "dose_mg_per_kg"),
            (self.weight_min_kg, self.weight_max_kg, "weight_kg"),
            (self.gfr_min_ml_min, self.gfr_max_ml_min, "gfr_ml_min"),
        ]
        for lo, hi, name in pairs:
            if lo is not None and hi is not None and lo > hi:
                raise ValueError(f"{name}: min must be <= max")
        if (self.dose_mg_per_kg_min is not None or self.dose_mg_per_kg_max is not None) and not self.per_kg_basis:
            raise ValueError("per_kg_basis ('per_dose' or 'per_day') is required for weight-based doses")
        if self.max_daily_dose_mg is not None and self.dose_mg_max is not None and self.max_daily_dose_period_hours == 24:
            if self.interval_hours and self.interval_hours > 0:
                per_day = self.dose_mg_max * Decimal(24) / self.interval_hours
                if per_day > self.max_daily_dose_mg * Decimal("1.0001"):
                    raise ValueError(
                        f"dose_mg_max at interval_hours implies {per_day:.0f} mg/24 h, above the stated ceiling "
                        f"{self.max_daily_dose_mg} mg/24 h"
                    )
        if not self.is_current_label and self.requires_human_verification is False:
            raise ValueError("a superseded label must remain flagged for human verification")
        return self


class DoseGuidelineCreate(DoseGuidelineBase, ProvenanceCreate):
    drug_id: uuid.UUID

    @model_validator(mode="after")
    def _only_official_sources_for_safety_doses(self) -> "DoseGuidelineCreate":
        if self.safety_critical and self.evidence_level not in {EvidenceLevel.A, EvidenceLevel.B}:
            raise ValueError("safety-critical dose rows need an official (A) or peer-reviewed (B) source")
        return self


class DoseGuidelineRead(DoseGuidelineBase, ProvenanceRead):
    model_config = ConfigDict(from_attributes=True, extra="ignore")
    id: uuid.UUID
    drug_id: uuid.UUID


# --------------------------------------------------------------------------
# Excipients & compatibility
# --------------------------------------------------------------------------
class ExcipientBase(APIModel):
    name: Name255
    synonyms: list[str] = Field(default_factory=list)
    cas_number: Optional[str] = None
    functions: list[str] = Field(default_factory=list)
    common_dosage_forms: list[str] = Field(default_factory=list)
    applications: Optional[str] = None
    typical_conc_min_pct: Optional[Decimal] = Field(None, ge=0, le=100)
    typical_conc_max_pct: Optional[Decimal] = Field(None, ge=0, le=100)
    typical_conc_basis: Optional[str] = Field(None, max_length=128)
    physicochemical: dict = Field(default_factory=dict)
    pharmacopoeial_status: dict = Field(default_factory=dict)
    regulatory_notes: Optional[str] = None

    _v_cas = field_validator("cas_number")(_validate_cas)

    @model_validator(mode="after")
    def _check(self) -> "ExcipientBase":
        lo, hi = self.typical_conc_min_pct, self.typical_conc_max_pct
        if lo is not None and hi is not None and lo > hi:
            raise ValueError("typical_conc_min_pct must be <= typical_conc_max_pct")
        if (lo is not None or hi is not None) and not self.typical_conc_basis:
            raise ValueError("typical_conc_basis (e.g. '% w/w, tablet') is required with a concentration range")
        return self


class ExcipientCreate(ExcipientBase, ProvenanceCreate):
    pass


class ExcipientRead(ExcipientBase, ProvenanceRead):
    model_config = ConfigDict(from_attributes=True, extra="ignore")
    id: uuid.UUID
    tenant_id: Optional[uuid.UUID] = None
    created_at: datetime


class ExcipientSummary(ReadModel):
    id: uuid.UUID
    name: str
    functions: list[str] = Field(default_factory=list)


class CompatibilityBase(APIModel):
    category: CompatibilityCategory
    reported_interaction: Optional[str] = None
    possible_mechanism: Optional[str] = None
    methods: list[str] = Field(default_factory=list)
    temperature_c: Optional[Decimal] = Field(None, ge=-273.15, le=1000)
    relative_humidity_pct: Optional[Decimal] = Field(None, ge=0, le=100)
    duration_text: Optional[str] = Field(None, max_length=128)
    drug_excipient_ratio: Optional[str] = Field(None, max_length=64)
    conditions_summary: Optional[str] = None
    formulation_context: Optional[str] = Field(None, max_length=255)
    is_indirect_evidence: bool = False
    is_experimental_excipient: bool = False
    publication_date: Optional[date] = None
    doi: Optional[str] = None
    pmid: Optional[str] = None
    conflict_flag: bool = False

    _v_doi = field_validator("doi")(_validate_doi)
    _v_pmid = field_validator("pmid")(_validate_pmid)

    @model_validator(mode="after")
    def _no_unconditional_compatibility(self) -> "CompatibilityBase":
        """'No evidence of interaction' must never be stored as 'compatible'."""
        if self.category == CompatibilityCategory.COMPATIBLE_UNDER_CONDITIONS:
            if not (self.methods or self.conditions_summary or self.formulation_context):
                raise ValueError(
                    "'compatible_under_conditions' requires methods, conditions_summary or formulation_context; "
                    "use 'insufficient_evidence' when no study exists"
                )
        if self.category == CompatibilityCategory.INSUFFICIENT_EVIDENCE and self.reported_interaction:
            raise ValueError("insufficient_evidence rows cannot carry a reported_interaction")
        if self.category in {CompatibilityCategory.POTENTIAL_INTERACTION,
                             CompatibilityCategory.INCOMPATIBLE_UNDER_CONDITIONS} and not self.reported_interaction:
            raise ValueError("interaction categories require reported_interaction")
        return self


class CompatibilityCreate(CompatibilityBase, ProvenanceCreate):
    drug_id: uuid.UUID
    excipient_id: uuid.UUID
    conflict_id: Optional[uuid.UUID] = None


class CompatibilityRead(CompatibilityBase, ProvenanceRead):
    model_config = ConfigDict(from_attributes=True, extra="ignore")
    id: uuid.UUID
    drug_id: uuid.UUID
    excipient_id: uuid.UUID
    excipient: ExcipientSummary
    conflict_id: Optional[uuid.UUID] = None

    @computed_field  # type: ignore[prop-decorator]
    @property
    def category_code(self) -> int:
        return COMPATIBILITY_CATEGORY_CODE[self.category]


class CompatibilityCheckRequest(APIModel):
    drug_id: uuid.UUID
    excipient_id: uuid.UUID


class CompatibilityCheckResponse(ReadModel):
    """Compatibility Engine output. `verdict` is derived, never stored."""

    drug_id: uuid.UUID
    excipient_id: uuid.UUID
    verdict: CompatibilityCategory
    evidence: list[CompatibilityRead]
    disclaimer: str = (
        "Results are specific to the listed conditions. 'No evidence found' is not proof of compatibility."
    )


# --------------------------------------------------------------------------
# Indian pharma
# --------------------------------------------------------------------------
class IndianBrandBase(APIModel):
    brand_name: Name255
    manufacturer: Optional[str] = Field(None, max_length=255)
    strength: Optional[str] = Field(None, max_length=64)
    dosage_form: Optional[str] = Field(None, max_length=64)
    route: Optional[str] = Field(None, max_length=32)
    pack_size: Optional[str] = Field(None, max_length=64)
    ip_labelled: Optional[bool] = None
    verification_status: BrandVerificationStatus = BrandVerificationStatus.UNVERIFIED
    manufacturer_conflict: bool = False
    conflicting_manufacturers: list[str] = Field(default_factory=list)
    cdsco_approval_ref: Optional[str] = Field(None, max_length=128)
    cdsco_approval_date: Optional[date] = None
    safety_alert_note: Optional[str] = None
    last_checked_on: Optional[date] = None
    mrp_inr: Optional[Decimal] = Field(None, ge=0, max_digits=12, decimal_places=2)

    @model_validator(mode="after")
    def _check(self) -> "IndianBrandBase":
        if self.verification_status == BrandVerificationStatus.CDSCO_VERIFIED and not self.cdsco_approval_ref:
            raise ValueError("cdsco_verified requires cdsco_approval_ref")
        if self.manufacturer_conflict and len(self.conflicting_manufacturers) < 2:
            raise ValueError("manufacturer_conflict requires at least two conflicting_manufacturers")
        return self


class IndianBrandCreate(IndianBrandBase, ProvenanceCreate):
    drug_id: uuid.UUID
    price_source_id: Optional[uuid.UUID] = None

    @model_validator(mode="after")
    def _price_and_level(self) -> "IndianBrandCreate":
        if self.mrp_inr is not None and self.price_source_id is None:
            raise ValueError("mrp_inr requires price_source_id (price must come from a legal, cited source)")
        if self.verification_status == BrandVerificationStatus.CDSCO_VERIFIED and self.evidence_level != EvidenceLevel.A:
            raise ValueError("cdsco_verified brands must cite an official (A) source")
        return self


class IndianBrandRead(IndianBrandBase, ProvenanceRead):
    model_config = ConfigDict(from_attributes=True, extra="ignore")
    id: uuid.UUID
    drug_id: uuid.UUID
    price_source_id: Optional[uuid.UUID] = None
    is_publishable: bool


# --------------------------------------------------------------------------
# Literature (pgvector)
# --------------------------------------------------------------------------
class LiteratureBase(APIModel):
    title: NonEmptyStr
    authors: list[str] = Field(default_factory=list)
    journal: Optional[str] = Field(None, max_length=255)
    publication_year: Optional[int] = Field(None, ge=1800, le=2100)
    study_type: Optional[str] = Field(None, max_length=128)
    doi: Optional[str] = None
    pmid: Optional[str] = None
    url: Optional[Annotated[str, StringConstraints(pattern=r"^https?://\S+$")]] = None
    abstract_summary: Optional[str] = None
    abstract_reuse_permitted: bool = False
    evidence_level: EvidenceLevel
    access_date: Optional[date] = None

    _v_doi = field_validator("doi")(_validate_doi)
    _v_pmid = field_validator("pmid")(_validate_pmid)

    @model_validator(mode="after")
    def _needs_identifier(self) -> "LiteratureBase":
        if not (self.doi or self.pmid or self.url):
            raise ValueError("a literature reference needs at least one of doi, pmid or url")
        return self


class LiteratureCreate(LiteratureBase):
    source_id: Optional[uuid.UUID] = None
    drug_ids: list[uuid.UUID] = Field(default_factory=list)
    section_tag: Optional[str] = Field(None, max_length=64)


class LiteratureRead(LiteratureBase, ReadModel):
    model_config = ConfigDict(from_attributes=True, extra="ignore")
    id: uuid.UUID
    tenant_id: Optional[uuid.UUID] = None
    source: Optional[SourceBrief] = None
    embedding_model: Optional[str] = None
    created_at: datetime

    @computed_field  # type: ignore[prop-decorator]
    @property
    def evidence_label(self) -> str:
        return EVIDENCE_LABELS[self.evidence_level]


class LiteratureSimilaritySearchRequest(APIModel):
    query: Annotated[str, StringConstraints(strip_whitespace=True, min_length=3, max_length=2000)]
    top_k: int = Field(10, ge=1, le=50)
    min_evidence_level: EvidenceLevel = EvidenceLevel.E
    drug_id: Optional[uuid.UUID] = None


class LiteratureHit(ReadModel):
    reference: LiteratureRead
    cosine_similarity: float = Field(ge=-1.0, le=1.0)


class DrugLiteratureLink(APIModel):
    literature_id: uuid.UUID
    section_tag: Optional[str] = Field(None, max_length=64)
    relevance_note: Optional[str] = None


# --------------------------------------------------------------------------
# Conflicts & missing data
# --------------------------------------------------------------------------
class ConflictLogBase(APIModel):
    field_name: Annotated[str, StringConstraints(min_length=1, max_length=128)]
    claim: NonEmptyStr
    source_1_id: Optional[uuid.UUID] = None
    source_1_statement: NonEmptyStr
    source_2_id: Optional[uuid.UUID] = None
    source_2_statement: NonEmptyStr
    difference: Optional[str] = None
    possible_reason: Optional[str] = None
    current_interpretation: Optional[str] = None
    confidence: ConfidenceLevel


class ConflictLogCreate(ConflictLogBase):
    drug_id: uuid.UUID


class ConflictResolveRequest(APIModel):
    current_interpretation: NonEmptyStr


class ConflictLogRead(ConflictLogBase, ReadModel):
    model_config = ConfigDict(from_attributes=True, extra="ignore")
    id: uuid.UUID
    drug_id: uuid.UUID
    resolved: bool
    resolved_by_user_id: Optional[uuid.UUID] = None
    resolved_at: Optional[datetime] = None
    source_1: Optional[SourceBrief] = None
    source_2: Optional[SourceBrief] = None


class MissingDataItemCreate(APIModel):
    drug_id: uuid.UUID
    field_name: Annotated[str, StringConstraints(min_length=1, max_length=128)]
    statement: NonEmptyStr
    suggested_next_step: Optional[str] = None
    searched_on: Optional[date] = None


class MissingDataItemRead(ReadModel):
    id: uuid.UUID
    drug_id: uuid.UUID
    field_name: str
    statement: str
    suggested_next_step: Optional[str] = None
    searched_on: Optional[date] = None
    is_resolved: bool


# --------------------------------------------------------------------------
# Aggregate profile (Drug Profile screen / RAG context)
# --------------------------------------------------------------------------
class LiteratureLinkRead(ReadModel):
    section_tag: Optional[str] = None
    relevance_note: Optional[str] = None
    literature: LiteratureRead


class DrugProfile(DrugRead):
    identifiers: list[DrugIdentifierRead] = Field(default_factory=list)
    preformulation_metrics: list[PreformulationMetricRead] = Field(default_factory=list)
    bcs_assessments: list[BCSAssessmentRead] = Field(default_factory=list)
    dose_guidelines: list[DoseGuidelineRead] = Field(default_factory=list)
    compatibilities: list[CompatibilityRead] = Field(default_factory=list)
    indian_brands: list[IndianBrandRead] = Field(default_factory=list)
    literature_links: list[LiteratureLinkRead] = Field(default_factory=list)
    conflicts: list[ConflictLogRead] = Field(default_factory=list)
    missing_data: list[MissingDataItemRead] = Field(default_factory=list)


# --------------------------------------------------------------------------
# RAG Provenance & Citation Engine
# --------------------------------------------------------------------------
class ProvenanceClaim(ReadModel):
    statement: str
    source_name: str
    source_locator: Optional[str] = None
    source_url: Optional[str] = None
    evidence_level: EvidenceLevel
    evidence_label: str
    confidence: ConfidenceLevel = ConfidenceLevel.HIGH
    conditions: Optional[dict] = None
    dispute_flag: bool = False


class RAGQueryRequest(APIModel):
    query: Annotated[str, StringConstraints(strip_whitespace=True, min_length=3, max_length=2000)]
    drug_id: Optional[uuid.UUID] = None
    top_k_literature: int = Field(5, ge=1, le=20)
    min_evidence_level: EvidenceLevel = EvidenceLevel.E


class RAGResponse(ReadModel):
    query: str
    answer_markdown: str
    claims: list[ProvenanceClaim]
    literature_citations: list[LiteratureHit]
    relational_entities_cited: list[str] = Field(default_factory=list)
    confidence: ConfidenceLevel
    disclaimer: str = (
        "AI synthesized response strictly mapped to verified sources in the DrugLab repository. "
        "Clinical and formulation decisions require independent validation against authoritative pharmacopoeial monographs."
    )

