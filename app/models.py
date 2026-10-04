"""DrugLab / DrugPedia - relational core (Phase 1).

Design rules taken from the four drug records (Ibuprofen, Paracetamol,
Amoxicillin, Azithromycin):

* Every important value carries provenance: source, evidence level (A-E),
  source date and a locator (e.g. "DailyMed 12.3 Table 11").
* Values keep their conditions (temperature, pH, ionic strength, method,
  solid form). One drug can hold several conflicting values for the same
  property; conflicts are first-class rows, never silently overwritten.
* "Not found" is data too: MissingDataItem rows replace invented values.
* "No interaction found" is not "compatible": the compatibility table has an
  explicit INSUFFICIENT_EVIDENCE category.
* Multi-tenancy: reference rows with tenant_id IS NULL are global (visible to
  everyone, writable only by platform admins); rows with a tenant_id are
  private to that tenant. Postgres row-level security is applied in
  database.py.
"""

import enum
import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pgvector.sqlalchemy import Vector
from sqlalchemy import (
    ARRAY,
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    Enum as SAEnum,
    ForeignKey,
    Index,
    Integer,
    MetaData,
    Numeric,
    SmallInteger,
    String,
    Text,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    declared_attr,
    mapped_column,
    relationship,
)

EMBEDDING_DIM = 1536  # change together with the embedding model
NIL_UUID = "00000000-0000-0000-0000-000000000000"

NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING_CONVENTION)


# --------------------------------------------------------------------------
# Enums
# --------------------------------------------------------------------------
class EvidenceLevel(str, enum.Enum):
    A = "A"  # Official / regulatory / government / pharmacopoeial
    B = "B"  # Peer-reviewed primary research
    C = "C"  # Authoritative scientific database
    D = "D"  # High-quality secondary source
    E = "E"  # Limited / commercial listing / other


class SourceType(str, enum.Enum):
    REGULATORY_LABEL = "regulatory_label"
    REGULATORY_COMMUNICATION = "regulatory_communication"
    PHARMACOPOEIAL = "pharmacopoeial"
    GOVERNMENT_LIST = "government_list"
    PEER_REVIEWED = "peer_reviewed"
    SCIENTIFIC_DATABASE = "scientific_database"
    SECONDARY_DATABASE = "secondary_database"
    PATENT = "patent"
    COMMERCIAL_LISTING = "commercial_listing"
    REPOSITORY_OR_THESIS = "repository_or_thesis"
    OTHER = "other"


class AccessDepth(str, enum.Enum):
    FULL_TEXT = "full_text"
    ABSTRACT_ONLY = "abstract_only"
    EXCERPT_ONLY = "excerpt_only"
    NOT_OPENED = "not_opened"


class RecordStatus(str, enum.Enum):
    DRAFT = "draft"
    PARTIALLY_VERIFIED = "partially_verified"
    HUMAN_VERIFIED = "human_verified"
    PUBLISHED = "published"


class FormTag(str, enum.Enum):
    """Salt / hydrate identity. Never merge data across forms."""

    PARENT = "parent"
    ANHYDROUS = "anhydrous"
    MONOHYDRATE = "monohydrate"
    DIHYDRATE = "dihydrate"
    TRIHYDRATE = "trihydrate"
    SODIUM_SALT = "sodium_salt"
    HYDROCHLORIDE = "hydrochloride"
    ENANTIOMER = "enantiomer"
    OTHER = "other"


class IdentifierType(str, enum.Enum):
    CAS = "cas"
    UNII = "unii"
    PUBCHEM_CID = "pubchem_cid"
    ATC = "atc"
    DRUGBANK = "drugbank"
    CHEMBL = "chembl"
    CHEBI = "chebi"
    RXNORM = "rxnorm"
    EC_NUMBER = "ec_number"
    IUPHAR = "iuphar"
    OTHER = "other"


class MetricType(str, enum.Enum):
    PKA = "pka"
    LOGP = "logp"
    LOGD = "logd"
    XLOGP3 = "xlogp3"
    MELTING_POINT = "melting_point"
    THERMAL_EVENT = "thermal_event"
    WATER_SOLUBILITY = "water_solubility"
    PH_SOLUBILITY = "ph_solubility"
    SOLVENT_SOLUBILITY = "solvent_solubility"
    DENSITY = "density"
    BULK_DENSITY = "bulk_density"
    PARTICLE_SIZE = "particle_size"
    FLOW_COMPRESSIBILITY = "flow_compressibility"
    HYGROSCOPICITY = "hygroscopicity"
    PHOTOSTABILITY = "photostability"
    SPECIFIC_ROTATION = "specific_rotation"
    TPSA = "tpsa"
    HBD = "hbd"
    HBA = "hba"
    ROTATABLE_BONDS = "rotatable_bonds"
    OTHER = "other"


class ValueOrigin(str, enum.Enum):
    EXPERIMENTAL = "experimental"
    COMPUTED = "computed"
    PREDICTED = "predicted"
    LABEL_STATEMENT = "label_statement"
    LITERATURE_REVIEW = "literature_review"
    SUPPLIER_DATUM = "supplier_datum"


class BCSClass(str, enum.Enum):
    I = "I"
    II = "II"
    III = "III"
    IV = "IV"


class CompatibilityCategory(str, enum.Enum):
    COMPATIBLE_UNDER_CONDITIONS = "compatible_under_conditions"  # category 1
    POTENTIAL_INTERACTION = "potential_interaction"  # category 2
    INCOMPATIBLE_UNDER_CONDITIONS = "incompatible_under_conditions"  # category 3
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"  # category 4


COMPATIBILITY_CATEGORY_CODE = {
    CompatibilityCategory.COMPATIBLE_UNDER_CONDITIONS: 1,
    CompatibilityCategory.POTENTIAL_INTERACTION: 2,
    CompatibilityCategory.INCOMPATIBLE_UNDER_CONDITIONS: 3,
    CompatibilityCategory.INSUFFICIENT_EVIDENCE: 4,
}


class ConfidenceLevel(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class BrandVerificationStatus(str, enum.Enum):
    UNVERIFIED = "unverified"  # commercial directory only
    MANUFACTURER_CONFIRMED = "manufacturer_confirmed"
    CDSCO_VERIFIED = "cdsco_verified"


class UserRole(str, enum.Enum):
    PLATFORM_ADMIN = "platform_admin"
    TENANT_ADMIN = "tenant_admin"
    EDITOR = "editor"
    REVIEWER = "reviewer"
    VIEWER = "viewer"


def pg_enum(enum_cls: type[enum.Enum]) -> SAEnum:
    """Native PG enum persisted by value (e.g. 'A', 'dihydrate')."""
    return SAEnum(
        enum_cls,
        name=enum_cls.__name__.lower(),
        values_callable=lambda e: [m.value for m in e],
        native_enum=True,
        validate_strings=True,
    )


# --------------------------------------------------------------------------
# Mixins
# --------------------------------------------------------------------------
class UUIDPrimaryKeyMixin:
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class TenantScopedMixin:
    """tenant_id NULL = global reference row; otherwise private to a tenant."""

    tenant_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )


class ProvenanceMixin:
    """Every claim row says where it came from and how much to trust it."""

    source_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("sources.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    evidence_level: Mapped[EvidenceLevel] = mapped_column(
        pg_enum(EvidenceLevel), nullable=False
    )
    source_locator: Mapped[Optional[str]] = mapped_column(String(255))
    source_date: Mapped[Optional[date]] = mapped_column(Date)

    @declared_attr
    def source(cls) -> Mapped["Source"]:  # noqa: N805
        return relationship("Source", lazy="joined", foreign_keys=f"[{cls.__name__}.source_id]")


# --------------------------------------------------------------------------
# Tenancy / identity
# --------------------------------------------------------------------------
class Tenant(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "tenants"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    plan: Mapped[str] = mapped_column(
        String(32), nullable=False, server_default="free"
    )  # free | professional | enterprise
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("true")
    )

    users: Mapped[list["User"]] = relationship(
        back_populates="tenant", cascade="all, delete-orphan", passive_deletes=True
    )


class User(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "users"

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    email: Mapped[str] = mapped_column(String(320), nullable=False, unique=True)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        pg_enum(UserRole), nullable=False, server_default=UserRole.VIEWER.value
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("true")
    )

    tenant: Mapped[Tenant] = relationship(back_populates="users")


# --------------------------------------------------------------------------
# Provenance
# --------------------------------------------------------------------------
class Source(UUIDPrimaryKeyMixin, TimestampMixin, TenantScopedMixin, Base):
    """One citable document / record / dataset (Provenance Table, Section 29)."""

    __tablename__ = "sources"

    name: Mapped[str] = mapped_column(String(500), nullable=False)
    document_title: Mapped[Optional[str]] = mapped_column(Text)
    url: Mapped[Optional[str]] = mapped_column(Text)
    source_type: Mapped[SourceType] = mapped_column(pg_enum(SourceType), nullable=False)
    default_evidence_level: Mapped[EvidenceLevel] = mapped_column(
        pg_enum(EvidenceLevel), nullable=False
    )
    version_or_edition: Mapped[Optional[str]] = mapped_column(String(255))
    record_id: Mapped[Optional[str]] = mapped_column(String(255))
    doi: Mapped[Optional[str]] = mapped_column(String(255), index=True)
    pmid: Mapped[Optional[str]] = mapped_column(String(16), index=True)
    publication_date: Mapped[Optional[date]] = mapped_column(Date)
    access_date: Mapped[Optional[date]] = mapped_column(Date)
    access_depth: Mapped[AccessDepth] = mapped_column(
        pg_enum(AccessDepth),
        nullable=False,
        server_default=AccessDepth.NOT_OPENED.value,
    )
    licence_status: Mapped[Optional[str]] = mapped_column(Text)
    is_mirror_or_aggregator: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("false")
    )
    notes: Mapped[Optional[str]] = mapped_column(Text)

    __table_args__ = (
        CheckConstraint("pmid IS NULL OR pmid ~ '^[0-9]{1,9}$'", name="pmid_format"),
        Index("ix_sources_url", "url", postgresql_using="hash"),
    )


# --------------------------------------------------------------------------
# Drugs
# --------------------------------------------------------------------------
class Drug(UUIDPrimaryKeyMixin, TimestampMixin, TenantScopedMixin, Base):
    """Module 1 drug profile. One row per drug *form* (parent, dihydrate, ...)."""

    __tablename__ = "drugs"

    # --- Section 1: identity
    generic_name: Mapped[str] = mapped_column(String(255), nullable=False)
    form_tag: Mapped[FormTag] = mapped_column(
        pg_enum(FormTag), nullable=False, server_default=FormTag.PARENT.value
    )
    form_description: Mapped[Optional[str]] = mapped_column(String(255))
    inn: Mapped[Optional[str]] = mapped_column(String(255))
    usan: Mapped[Optional[str]] = mapped_column(String(255))
    ban: Mapped[Optional[str]] = mapped_column(String(255))
    us_name: Mapped[Optional[str]] = mapped_column(String(255))  # e.g. acetaminophen
    synonyms: Mapped[list[str]] = mapped_column(
        ARRAY(Text), nullable=False, server_default=text("'{}'::text[]")
    )
    therapeutic_class: Mapped[Optional[str]] = mapped_column(String(255))
    pharmacological_class: Mapped[Optional[str]] = mapped_column(String(255))
    chemical_class: Mapped[Optional[str]] = mapped_column(String(255))
    atc_code: Mapped[Optional[str]] = mapped_column(String(7), index=True)
    cas_number: Mapped[Optional[str]] = mapped_column(String(12), index=True)
    unii: Mapped[Optional[str]] = mapped_column(String(10))
    pubchem_cid: Mapped[Optional[int]] = mapped_column(Integer, index=True)
    active_moiety: Mapped[Optional[str]] = mapped_column(String(255))
    is_prodrug: Mapped[Optional[bool]] = mapped_column(Boolean)

    # --- Section 2: chemistry
    iupac_name: Mapped[Optional[str]] = mapped_column(Text)
    molecular_formula: Mapped[Optional[str]] = mapped_column(String(128))
    molecular_weight: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 3))
    exact_mass: Mapped[Optional[Decimal]] = mapped_column(Numeric(14, 9))
    smiles_isomeric: Mapped[Optional[str]] = mapped_column(Text)
    smiles_canonical: Mapped[Optional[str]] = mapped_column(Text)
    inchi: Mapped[Optional[str]] = mapped_column(Text)
    inchikey: Mapped[Optional[str]] = mapped_column(String(27), index=True)
    stereocentre_count: Mapped[Optional[int]] = mapped_column(SmallInteger)
    stereochemistry_note: Mapped[Optional[str]] = mapped_column(Text)
    functional_groups: Mapped[list[str]] = mapped_column(
        ARRAY(Text), nullable=False, server_default=text("'{}'::text[]")
    )

    # --- Pharmacology summary (Module 1)
    mechanism_of_action: Mapped[Optional[str]] = mapped_column(Text)
    pharmacological_action: Mapped[Optional[str]] = mapped_column(Text)

    # --- Record governance
    scope_note: Mapped[Optional[str]] = mapped_column(Text)
    record_status: Mapped[RecordStatus] = mapped_column(
        pg_enum(RecordStatus), nullable=False, server_default=RecordStatus.DRAFT.value
    )
    date_researched: Mapped[Optional[date]] = mapped_column(Date)
    date_last_verified: Mapped[Optional[date]] = mapped_column(Date)
    verified_by_user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL")
    )
    verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    identity_source_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("sources.id", ondelete="SET NULL")
    )
    identity_evidence_level: Mapped[Optional[EvidenceLevel]] = mapped_column(
        pg_enum(EvidenceLevel)
    )

    identity_source: Mapped[Optional[Source]] = relationship(
        foreign_keys=[identity_source_id], lazy="joined"
    )
    identifiers: Mapped[list["DrugIdentifier"]] = relationship(
        back_populates="drug", cascade="all, delete-orphan", passive_deletes=True
    )
    preformulation_metrics: Mapped[list["PreformulationMetric"]] = relationship(
        back_populates="drug", cascade="all, delete-orphan", passive_deletes=True
    )
    bcs_assessments: Mapped[list["BCSAssessment"]] = relationship(
        back_populates="drug", cascade="all, delete-orphan", passive_deletes=True
    )
    dose_guidelines: Mapped[list["DoseGuideline"]] = relationship(
        back_populates="drug", cascade="all, delete-orphan", passive_deletes=True
    )
    compatibilities: Mapped[list["DrugExcipientCompatibility"]] = relationship(
        back_populates="drug", cascade="all, delete-orphan", passive_deletes=True
    )
    indian_brands: Mapped[list["IndianPharmaBrand"]] = relationship(
        back_populates="drug", cascade="all, delete-orphan", passive_deletes=True
    )
    literature_links: Mapped[list["DrugLiterature"]] = relationship(
        back_populates="drug", cascade="all, delete-orphan", passive_deletes=True
    )
    conflicts: Mapped[list["ConflictLog"]] = relationship(
        back_populates="drug", cascade="all, delete-orphan", passive_deletes=True
    )
    missing_data: Mapped[list["MissingDataItem"]] = relationship(
        back_populates="drug", cascade="all, delete-orphan", passive_deletes=True
    )

    @property
    def open_conflict_count(self) -> int:
        return sum(1 for c in self.conflicts if not c.resolved)

    __table_args__ = (
        CheckConstraint("molecular_weight IS NULL OR molecular_weight > 0", name="mw_positive"),
        CheckConstraint("exact_mass IS NULL OR exact_mass > 0", name="exact_mass_positive"),
        CheckConstraint(
            "inchikey IS NULL OR inchikey ~ '^[A-Z]{14}-[A-Z]{10}-[A-Z]$'",
            name="inchikey_format",
        ),
        CheckConstraint(
            "cas_number IS NULL OR cas_number ~ '^[0-9]{2,7}-[0-9]{2}-[0-9]$'",
            name="cas_format",
        ),
        CheckConstraint(
            "atc_code IS NULL OR atc_code ~ '^[A-Z][0-9]{2}[A-Z]{2}[0-9]{2}$'",
            name="atc_format",
        ),
        CheckConstraint(
            "stereocentre_count IS NULL OR stereocentre_count >= 0",
            name="stereocentre_nonneg",
        ),
        CheckConstraint(
            "record_status NOT IN ('human_verified','published') "
            "OR (verified_by_user_id IS NOT NULL AND date_last_verified IS NOT NULL)",
            name="verified_requires_reviewer",
        ),
        Index(
            "uq_drugs_scope_name_form",
            text(f"coalesce(tenant_id, '{NIL_UUID}'::uuid)"),
            "generic_name",
            "form_tag",
            unique=True,
        ),
        Index(
            "ix_drugs_generic_name_trgm",
            "generic_name",
            postgresql_using="gin",
            postgresql_ops={"generic_name": "gin_trgm_ops"},
        ),
    )


class DrugIdentifier(UUIDPrimaryKeyMixin, TimestampMixin, TenantScopedMixin, ProvenanceMixin, Base):
    """Secondary identifiers, e.g. ibuprofen CAS 58560-75-1 (racemate record),
    azithromycin dihydrate CAS 117772-70-0, UNII per hydrate."""

    __tablename__ = "drug_identifiers"

    drug_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("drugs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    id_type: Mapped[IdentifierType] = mapped_column(pg_enum(IdentifierType), nullable=False)
    value: Mapped[str] = mapped_column(String(128), nullable=False)
    applies_to_form: Mapped[Optional[FormTag]] = mapped_column(pg_enum(FormTag))
    note: Mapped[Optional[str]] = mapped_column(Text)

    drug: Mapped[Drug] = relationship(back_populates="identifiers")

    __table_args__ = (
        UniqueConstraint("drug_id", "id_type", "value", name="drug_idtype_value"),
        Index("ix_drug_identifiers_value", "id_type", "value"),
    )


# --------------------------------------------------------------------------
# Preformulation
# --------------------------------------------------------------------------
class PreformulationMetric(UUIDPrimaryKeyMixin, TimestampMixin, TenantScopedMixin, ProvenanceMixin, Base):
    """Module 2. One measured / computed value with its conditions.

    Example rows (from the records):
      amoxicillin pKa  2.4 / 7.4 / 9.6 at 22 C  (ionizable_group COOH / NH2 / OH, ordinal 1..3)
      amoxicillin water solubility 3.55 mg/mL, pH 4.5, 37 C
      ibuprofen melting point 74-77 C (value_min/value_max)
      paracetamol XLogP3 0.5 (origin 'computed')
    """

    __tablename__ = "preformulation_metrics"

    drug_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("drugs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    metric_type: Mapped[MetricType] = mapped_column(pg_enum(MetricType), nullable=False)
    metric_label: Mapped[Optional[str]] = mapped_column(String(128))  # for MetricType.OTHER / subtypes
    value_numeric: Mapped[Optional[Decimal]] = mapped_column(Numeric(18, 6))
    value_min: Mapped[Optional[Decimal]] = mapped_column(Numeric(18, 6))
    value_max: Mapped[Optional[Decimal]] = mapped_column(Numeric(18, 6))
    value_text: Mapped[Optional[str]] = mapped_column(Text)  # descriptive values ("practically insoluble")
    unit: Mapped[Optional[str]] = mapped_column(String(32))
    origin: Mapped[ValueOrigin] = mapped_column(pg_enum(ValueOrigin), nullable=False)

    # conditions
    temperature_c: Mapped[Optional[Decimal]] = mapped_column(Numeric(6, 2))
    ph: Mapped[Optional[Decimal]] = mapped_column(Numeric(4, 2))
    ionic_strength: Mapped[Optional[Decimal]] = mapped_column(Numeric(8, 4))
    medium: Mapped[Optional[str]] = mapped_column(String(255))
    method: Mapped[Optional[str]] = mapped_column(String(255))
    solid_form: Mapped[Optional[str]] = mapped_column(String(64))
    ionizable_group: Mapped[Optional[str]] = mapped_column(String(32))  # COOH | NH2 | OH | ...
    pka_ordinal: Mapped[Optional[int]] = mapped_column(SmallInteger)

    # integrity
    conflict_flag: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("false")
    )
    conflict_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("conflict_logs.id", ondelete="SET NULL")
    )
    notes: Mapped[Optional[str]] = mapped_column(Text)

    drug: Mapped[Drug] = relationship(back_populates="preformulation_metrics")
    conflict: Mapped[Optional["ConflictLog"]] = relationship(foreign_keys=[conflict_id])

    __table_args__ = (
        CheckConstraint(
            "value_numeric IS NOT NULL OR value_min IS NOT NULL OR value_max IS NOT NULL "
            "OR value_text IS NOT NULL",
            name="has_value",
        ),
        CheckConstraint(
            "value_min IS NULL OR value_max IS NULL OR value_min <= value_max",
            name="range_order",
        ),
        CheckConstraint(
            "pka_ordinal IS NULL OR (pka_ordinal BETWEEN 1 AND 5)", name="pka_ordinal_range"
        ),
        CheckConstraint(
            "metric_type <> 'pka' OR value_numeric BETWEEN -5 AND 25 "
            "OR value_min BETWEEN -5 AND 25",
            name="pka_plausible",
        ),
        CheckConstraint("ph IS NULL OR ph BETWEEN 0 AND 14", name="ph_range"),
        CheckConstraint(
            "conflict_id IS NULL OR conflict_flag", name="conflict_id_requires_flag"
        ),
        Index("ix_preform_drug_metric", "drug_id", "metric_type"),
    )


class BCSAssessment(UUIDPrimaryKeyMixin, TimestampMixin, TenantScopedMixin, ProvenanceMixin, Base):
    """BCS is source/dose dependent and sometimes disputed - one row per claim.

    Amoxicillin: I (<=875 mg), II (1000 mg), IV (>1000 mg).
    Paracetamol: III (2006 biowaiver) vs I (2024 rDCS) - both kept.
    Azithromycin: reported II, disputed.
    """

    __tablename__ = "bcs_assessments"

    drug_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("drugs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    bcs_class: Mapped[Optional[BCSClass]] = mapped_column(pg_enum(BCSClass))
    framework: Mapped[Optional[str]] = mapped_column(String(255))  # WHO biowaiver, FDA, provisional, rDCS...
    dose_mg_min: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    dose_mg_max: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    solubility_basis: Mapped[Optional[str]] = mapped_column(Text)
    permeability_basis: Mapped[Optional[str]] = mapped_column(Text)
    is_disputed: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))
    is_regulatory_classification: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("false")
    )
    rationale: Mapped[Optional[str]] = mapped_column(Text)
    conflict_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("conflict_logs.id", ondelete="SET NULL")
    )

    drug: Mapped[Drug] = relationship(back_populates="bcs_assessments")
    conflict: Mapped[Optional["ConflictLog"]] = relationship(foreign_keys=[conflict_id])

    __table_args__ = (
        CheckConstraint(
            "dose_mg_min IS NULL OR dose_mg_max IS NULL OR dose_mg_min <= dose_mg_max",
            name="dose_range_order",
        ),
    )


# --------------------------------------------------------------------------
# Dose tracking (dose ceilings, renal bands, paediatric weight bands)
# --------------------------------------------------------------------------
class DoseGuideline(UUIDPrimaryKeyMixin, TimestampMixin, TenantScopedMixin, ProvenanceMixin, Base):
    """Reference dosing from a specific label. Never a substitute for the label.

    Paracetamol: max_daily_dose_mg 4000 per 24 h (FDA OTC example).
    Amoxicillin: renal band gfr 10-30 -> 500/250 mg q12h; GFR<30 no 875 mg.
    """

    __tablename__ = "dose_guidelines"

    drug_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("drugs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    population: Mapped[str] = mapped_column(String(128), nullable=False)  # adult, child >3 mo, neonate...
    route: Mapped[str] = mapped_column(String(32), nullable=False)  # oral | iv | rectal ...
    indication: Mapped[Optional[str]] = mapped_column(String(255))
    regimen_text: Mapped[str] = mapped_column(Text, nullable=False)

    dose_mg_min: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    dose_mg_max: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    dose_mg_per_kg_min: Mapped[Optional[Decimal]] = mapped_column(Numeric(8, 3))
    dose_mg_per_kg_max: Mapped[Optional[Decimal]] = mapped_column(Numeric(8, 3))
    per_kg_basis: Mapped[Optional[str]] = mapped_column(String(16))  # per_dose | per_day
    interval_hours: Mapped[Optional[Decimal]] = mapped_column(Numeric(6, 2))
    duration_days: Mapped[Optional[Decimal]] = mapped_column(Numeric(6, 1))

    max_daily_dose_mg: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    max_daily_dose_period_hours: Mapped[Optional[int]] = mapped_column(
        SmallInteger, server_default=text("24")
    )
    weight_min_kg: Mapped[Optional[Decimal]] = mapped_column(Numeric(6, 2))
    weight_max_kg: Mapped[Optional[Decimal]] = mapped_column(Numeric(6, 2))
    gfr_min_ml_min: Mapped[Optional[Decimal]] = mapped_column(Numeric(6, 1))
    gfr_max_ml_min: Mapped[Optional[Decimal]] = mapped_column(Numeric(6, 1))

    jurisdiction: Mapped[str] = mapped_column(String(32), nullable=False)  # US, UK, EU, IN, WHO
    product_context: Mapped[Optional[str]] = mapped_column(String(255))
    label_revision_date: Mapped[Optional[date]] = mapped_column(Date)
    is_current_label: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("true"))
    is_product_specific: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("true"))
    safety_critical: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("true"))
    requires_human_verification: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("true")
    )

    drug: Mapped[Drug] = relationship(back_populates="dose_guidelines")

    __table_args__ = (
        CheckConstraint("max_daily_dose_mg IS NULL OR max_daily_dose_mg > 0", name="ceiling_positive"),
        CheckConstraint(
            "max_daily_dose_mg IS NULL OR max_daily_dose_period_hours IS NOT NULL",
            name="ceiling_needs_period",
        ),
        CheckConstraint(
            "dose_mg_min IS NULL OR dose_mg_max IS NULL OR dose_mg_min <= dose_mg_max",
            name="dose_range_order",
        ),
        CheckConstraint(
            "dose_mg_per_kg_min IS NULL OR dose_mg_per_kg_max IS NULL "
            "OR dose_mg_per_kg_min <= dose_mg_per_kg_max",
            name="perkg_range_order",
        ),
        CheckConstraint(
            "weight_min_kg IS NULL OR weight_max_kg IS NULL OR weight_min_kg <= weight_max_kg",
            name="weight_range_order",
        ),
        CheckConstraint(
            "gfr_min_ml_min IS NULL OR gfr_max_ml_min IS NULL OR gfr_min_ml_min <= gfr_max_ml_min",
            name="gfr_range_order",
        ),
        Index("ix_dose_drug_jurisdiction", "drug_id", "jurisdiction"),
    )


# --------------------------------------------------------------------------
# Excipients & compatibility
# --------------------------------------------------------------------------
class Excipient(UUIDPrimaryKeyMixin, TimestampMixin, TenantScopedMixin, ProvenanceMixin, Base):
    """Module 3 excipient library."""

    __tablename__ = "excipients"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    synonyms: Mapped[list[str]] = mapped_column(
        ARRAY(Text), nullable=False, server_default=text("'{}'::text[]")
    )
    cas_number: Mapped[Optional[str]] = mapped_column(String(12))
    functions: Mapped[list[str]] = mapped_column(
        ARRAY(Text), nullable=False, server_default=text("'{}'::text[]")
    )  # diluent, binder, lubricant, disintegrant...
    common_dosage_forms: Mapped[list[str]] = mapped_column(
        ARRAY(Text), nullable=False, server_default=text("'{}'::text[]")
    )
    applications: Mapped[Optional[str]] = mapped_column(Text)
    typical_conc_min_pct: Mapped[Optional[Decimal]] = mapped_column(Numeric(7, 3))
    typical_conc_max_pct: Mapped[Optional[Decimal]] = mapped_column(Numeric(7, 3))
    typical_conc_basis: Mapped[Optional[str]] = mapped_column(String(128))  # e.g. "% w/w, tablet"
    physicochemical: Mapped[dict] = mapped_column(
        JSONB, nullable=False, server_default=text("'{}'::jsonb")
    )
    pharmacopoeial_status: Mapped[dict] = mapped_column(
        JSONB, nullable=False, server_default=text("'{}'::jsonb")
    )  # {"USP": "...", "IP": "...", "Ph.Eur.": "..."} - status only, no protected text
    regulatory_notes: Mapped[Optional[str]] = mapped_column(Text)

    compatibilities: Mapped[list["DrugExcipientCompatibility"]] = relationship(
        back_populates="excipient", cascade="all, delete-orphan", passive_deletes=True
    )

    __table_args__ = (
        CheckConstraint(
            "cas_number IS NULL OR cas_number ~ '^[0-9]{2,7}-[0-9]{2}-[0-9]$'", name="cas_format"
        ),
        CheckConstraint(
            "typical_conc_min_pct IS NULL OR typical_conc_max_pct IS NULL "
            "OR typical_conc_min_pct <= typical_conc_max_pct",
            name="conc_range_order",
        ),
        Index(
            "uq_excipients_scope_name",
            text(f"coalesce(tenant_id, '{NIL_UUID}'::uuid)"),
            text("lower(name)"),
            unique=True,
        ),
        Index(
            "ix_excipients_name_trgm",
            "name",
            postgresql_using="gin",
            postgresql_ops={"name": "gin_trgm_ops"},
        ),
    )


class DrugExcipientCompatibility(UUIDPrimaryKeyMixin, TimestampMixin, TenantScopedMixin, ProvenanceMixin, Base):
    """Compatibility Engine evidence row. One row per study / observation.

    Rules baked into the schema:
      * category 'compatible_under_conditions' is never 'universally compatible';
      * co-existence in a marketed product is recorded as is_indirect_evidence=True;
      * absence of a study is represented by INSUFFICIENT_EVIDENCE, not by a row saying compatible.
    """

    __tablename__ = "drug_excipient_compatibility"

    drug_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("drugs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    excipient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("excipients.id", ondelete="CASCADE"), nullable=False, index=True
    )
    category: Mapped[CompatibilityCategory] = mapped_column(
        pg_enum(CompatibilityCategory), nullable=False
    )
    reported_interaction: Mapped[Optional[str]] = mapped_column(Text)
    possible_mechanism: Mapped[Optional[str]] = mapped_column(Text)
    methods: Mapped[list[str]] = mapped_column(
        ARRAY(Text), nullable=False, server_default=text("'{}'::text[]")
    )  # FTIR, DSC, TG/DTG, XRPD, HPLC, ATR-IR, Raman...
    temperature_c: Mapped[Optional[Decimal]] = mapped_column(Numeric(6, 2))
    relative_humidity_pct: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2))
    duration_text: Mapped[Optional[str]] = mapped_column(String(128))
    drug_excipient_ratio: Mapped[Optional[str]] = mapped_column(String(64))  # "1:1 w/w", "0.25-5% w/w"
    conditions_summary: Mapped[Optional[str]] = mapped_column(Text)
    formulation_context: Mapped[Optional[str]] = mapped_column(String(255))
    is_indirect_evidence: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("false")
    )
    is_experimental_excipient: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("false")
    )
    publication_date: Mapped[Optional[date]] = mapped_column(Date)
    doi: Mapped[Optional[str]] = mapped_column(String(255))
    pmid: Mapped[Optional[str]] = mapped_column(String(16))
    conflict_flag: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))
    conflict_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("conflict_logs.id", ondelete="SET NULL")
    )

    drug: Mapped[Drug] = relationship(back_populates="compatibilities")
    excipient: Mapped[Excipient] = relationship(back_populates="compatibilities", lazy="joined")
    conflict: Mapped[Optional["ConflictLog"]] = relationship(foreign_keys=[conflict_id])

    @property
    def category_code(self) -> int:
        return COMPATIBILITY_CATEGORY_CODE[self.category]

    __table_args__ = (
        CheckConstraint(
            "category <> 'compatible_under_conditions' OR ("
            "cardinality(methods) > 0 OR conditions_summary IS NOT NULL "
            "OR formulation_context IS NOT NULL)",
            name="compatible_needs_conditions",
        ),
        CheckConstraint("relative_humidity_pct IS NULL OR relative_humidity_pct BETWEEN 0 AND 100", name="rh_range"),
        Index("ix_compat_pair", "drug_id", "excipient_id"),
    )


# --------------------------------------------------------------------------
# Indian pharma
# --------------------------------------------------------------------------
class IndianPharmaBrand(UUIDPrimaryKeyMixin, TimestampMixin, TenantScopedMixin, ProvenanceMixin, Base):
    """Module 6. Brand rows from commercial directories are level E and
    UNVERIFIED by default; they may only be published once verified."""

    __tablename__ = "indian_pharma_brands"

    drug_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("drugs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    brand_name: Mapped[str] = mapped_column(String(255), nullable=False)
    manufacturer: Mapped[Optional[str]] = mapped_column(String(255))
    strength: Mapped[Optional[str]] = mapped_column(String(64))
    dosage_form: Mapped[Optional[str]] = mapped_column(String(64))
    route: Mapped[Optional[str]] = mapped_column(String(32))
    pack_size: Mapped[Optional[str]] = mapped_column(String(64))
    ip_labelled: Mapped[Optional[bool]] = mapped_column(Boolean)  # "Tablets IP"
    verification_status: Mapped[BrandVerificationStatus] = mapped_column(
        pg_enum(BrandVerificationStatus),
        nullable=False,
        server_default=BrandVerificationStatus.UNVERIFIED.value,
    )
    manufacturer_conflict: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("false")
    )  # e.g. Wymox: Wockhardt vs Abbott
    conflicting_manufacturers: Mapped[list[str]] = mapped_column(
        ARRAY(Text), nullable=False, server_default=text("'{}'::text[]")
    )
    cdsco_approval_ref: Mapped[Optional[str]] = mapped_column(String(128))
    cdsco_approval_date: Mapped[Optional[date]] = mapped_column(Date)
    safety_alert_note: Mapped[Optional[str]] = mapped_column(Text)
    last_checked_on: Mapped[Optional[date]] = mapped_column(Date)
    mrp_inr: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2))
    price_source_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("sources.id", ondelete="SET NULL")
    )

    drug: Mapped[Drug] = relationship(back_populates="indian_brands")

    @property
    def is_publishable(self) -> bool:
        return (
            self.verification_status != BrandVerificationStatus.UNVERIFIED
            and not self.manufacturer_conflict
        )

    __table_args__ = (
        CheckConstraint(
            "mrp_inr IS NULL OR (mrp_inr >= 0 AND price_source_id IS NOT NULL)",
            name="price_needs_source",
        ),
        CheckConstraint(
            "verification_status <> 'cdsco_verified' OR cdsco_approval_ref IS NOT NULL",
            name="cdsco_needs_reference",
        ),
        Index(
            "ix_brands_name_trgm",
            "brand_name",
            postgresql_using="gin",
            postgresql_ops={"brand_name": "gin_trgm_ops"},
        ),
        Index("ix_brands_drug_brand", "drug_id", "brand_name"),
    )


# --------------------------------------------------------------------------
# Literature (pgvector)
# --------------------------------------------------------------------------
class LiteratureReference(UUIDPrimaryKeyMixin, TimestampMixin, TenantScopedMixin, Base):
    """Module 7. Metadata + OUR OWN summary + embedding. We never store
    publisher abstracts unless abstract_reuse_permitted is true."""

    __tablename__ = "literature_references"

    title: Mapped[str] = mapped_column(Text, nullable=False)
    authors: Mapped[list[str]] = mapped_column(
        ARRAY(Text), nullable=False, server_default=text("'{}'::text[]")
    )
    journal: Mapped[Optional[str]] = mapped_column(String(255))
    publication_year: Mapped[Optional[int]] = mapped_column(SmallInteger)
    study_type: Mapped[Optional[str]] = mapped_column(String(128))
    doi: Mapped[Optional[str]] = mapped_column(String(255))
    pmid: Mapped[Optional[str]] = mapped_column(String(16))
    url: Mapped[Optional[str]] = mapped_column(Text)
    abstract_summary: Mapped[Optional[str]] = mapped_column(Text)  # original-wording summary
    abstract_reuse_permitted: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("false")
    )
    evidence_level: Mapped[EvidenceLevel] = mapped_column(pg_enum(EvidenceLevel), nullable=False)
    source_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("sources.id", ondelete="SET NULL")
    )
    access_date: Mapped[Optional[date]] = mapped_column(Date)

    embedding: Mapped[Optional[list[float]]] = mapped_column(Vector(EMBEDDING_DIM))
    embedding_model: Mapped[Optional[str]] = mapped_column(String(128))
    embedding_content_hash: Mapped[Optional[str]] = mapped_column(String(64))
    embedding_updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    source: Mapped[Optional[Source]] = relationship(foreign_keys=[source_id], lazy="joined")
    drug_links: Mapped[list["DrugLiterature"]] = relationship(
        back_populates="literature", cascade="all, delete-orphan", passive_deletes=True
    )

    __table_args__ = (
        CheckConstraint(
            "publication_year IS NULL OR publication_year BETWEEN 1800 AND 2100", name="year_range"
        ),
        CheckConstraint("pmid IS NULL OR pmid ~ '^[0-9]{1,9}$'", name="pmid_format"),
        CheckConstraint(
            "embedding IS NULL OR embedding_model IS NOT NULL", name="embedding_needs_model"
        ),
        Index(
            "uq_literature_scope_doi",
            text(f"coalesce(tenant_id, '{NIL_UUID}'::uuid)"),
            "doi",
            unique=True,
            postgresql_where=text("doi IS NOT NULL"),
        ),
        Index(
            "uq_literature_scope_pmid",
            text(f"coalesce(tenant_id, '{NIL_UUID}'::uuid)"),
            "pmid",
            unique=True,
            postgresql_where=text("pmid IS NOT NULL"),
        ),
        Index(
            "ix_literature_embedding_hnsw",
            "embedding",
            postgresql_using="hnsw",
            postgresql_with={"m": 16, "ef_construction": 64},
            postgresql_ops={"embedding": "vector_cosine_ops"},
        ),
    )


class DrugLiterature(TimestampMixin, TenantScopedMixin, Base):
    """Drug <-> literature link (many-to-many)."""

    __tablename__ = "drug_literature"

    drug_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("drugs.id", ondelete="CASCADE"), primary_key=True
    )
    literature_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("literature_references.id", ondelete="CASCADE"),
        primary_key=True,
    )
    section_tag: Mapped[Optional[str]] = mapped_column(String(64))  # compatibility, bcs, stability...
    relevance_note: Mapped[Optional[str]] = mapped_column(Text)

    drug: Mapped[Drug] = relationship(back_populates="literature_links")
    literature: Mapped[LiteratureReference] = relationship(back_populates="drug_links", lazy="joined")


# --------------------------------------------------------------------------
# Conflict log & missing data
# --------------------------------------------------------------------------
class ConflictLog(UUIDPrimaryKeyMixin, TimestampMixin, TenantScopedMixin, Base):
    """Section 30. Conflicts are retained and resolved only on human review
    (e.g. paracetamol BCS III vs I; amoxicillin pKa 2.4/7.4/9.6 vs 4.77/9.29)."""

    __tablename__ = "conflict_logs"

    drug_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("drugs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    field_name: Mapped[str] = mapped_column(String(128), nullable=False)
    claim: Mapped[str] = mapped_column(Text, nullable=False)
    source_1_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("sources.id", ondelete="SET NULL")
    )
    source_1_statement: Mapped[str] = mapped_column(Text, nullable=False)
    source_2_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("sources.id", ondelete="SET NULL")
    )
    source_2_statement: Mapped[str] = mapped_column(Text, nullable=False)
    difference: Mapped[Optional[str]] = mapped_column(Text)
    possible_reason: Mapped[Optional[str]] = mapped_column(Text)
    current_interpretation: Mapped[Optional[str]] = mapped_column(Text)
    confidence: Mapped[ConfidenceLevel] = mapped_column(pg_enum(ConfidenceLevel), nullable=False)
    resolved: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))
    resolved_by_user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL")
    )
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    drug: Mapped[Drug] = relationship(back_populates="conflicts")
    source_1: Mapped[Optional[Source]] = relationship(foreign_keys=[source_1_id], lazy="joined")
    source_2: Mapped[Optional[Source]] = relationship(foreign_keys=[source_2_id], lazy="joined")

    __table_args__ = (
        CheckConstraint(
            "NOT resolved OR (resolved_by_user_id IS NOT NULL AND resolved_at IS NOT NULL)",
            name="resolved_needs_reviewer",
        ),
    )


class MissingDataItem(UUIDPrimaryKeyMixin, TimestampMixin, TenantScopedMixin, Base):
    """Section 31. Explicit 'not found' rows - fields are never filled with estimates."""

    __tablename__ = "missing_data_items"

    drug_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("drugs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    field_name: Mapped[str] = mapped_column(String(128), nullable=False)
    statement: Mapped[str] = mapped_column(Text, nullable=False)
    suggested_next_step: Mapped[Optional[str]] = mapped_column(Text)
    searched_on: Mapped[Optional[date]] = mapped_column(Date)
    is_resolved: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))

    drug: Mapped[Drug] = relationship(back_populates="missing_data")

    __table_args__ = (UniqueConstraint("drug_id", "field_name", name="drug_field"),)
