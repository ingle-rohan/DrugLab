"""DrugLab / DrugPedia - Drug Catalog & Profile API Routes.

Implements:
- Drug search with multi-parameter filtering (text, ATC, BCS, therapeutic class)
- Drug listing with pagination
- Full drug profile retrieval with complete provenance, preformulation metrics,
  compatibility records, dosing guidelines, conflicts, and missing data items.
"""

import uuid
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import any_, func, or_, select
from sqlalchemy.orm import selectinload

from ..dependencies import DatabaseDep, TenantDep
from ..models import (
    BCSAssessment,
    BCSClass,
    ConflictLog,
    DoseGuideline,
    Drug,
    DrugExcipientCompatibility,
    DrugIdentifier,
    DrugLiterature,
    IndianPharmaBrand,
    LiteratureReference,
    MissingDataItem,
    PreformulationMetric,
    RecordStatus,
)
from ..schemas import DrugProfile, DrugSummary, Page

router = APIRouter(prefix="/drugs", tags=["Drugs"])


@router.get(
    "/search",
    response_model=Page[DrugSummary],
    summary="Search drugs by text, identifiers, ATC, or BCS class",
)
def search_drugs(
    db: DatabaseDep,
    ctx: TenantDep,
    q: Annotated[Optional[str], Query(description="Search term (name, synonym, CAS, ATC, InChIKey)")] = None,
    atc: Annotated[Optional[str], Query(description="ATC code filter prefix (e.g., M01, J01)")] = None,
    bcs_class: Annotated[Optional[BCSClass], Query(description="BCS class filter")] = None,
    therapeutic_class: Annotated[Optional[str], Query(description="Therapeutic category filter")] = None,
    record_status: Annotated[Optional[RecordStatus], Query(description="Record status filter")] = None,
    offset: Annotated[int, Query(ge=0, description="Pagination offset")] = 0,
    limit: Annotated[int, Query(ge=1, le=100, description="Items per page")] = 25,
) -> Page[DrugSummary]:
    """Search the drug library within the caller's tenant context.

    Returns global drug records plus any tenant-private records visible to the current tenant.
    """
    stmt = select(Drug)

    # Free-text search across primary name, synonyms, CAS, ATC, and InChIKey
    if q:
        search_pattern = f"%{q.strip()}%"
        stmt = stmt.where(
            or_(
                Drug.generic_name.ilike(search_pattern),
                Drug.inn.ilike(search_pattern),
                Drug.usan.ilike(search_pattern),
                Drug.us_name.ilike(search_pattern),
                Drug.cas_number.ilike(search_pattern),
                Drug.atc_code.ilike(search_pattern),
                Drug.inchikey.ilike(search_pattern),
                func.array_to_string(Drug.synonyms, " ").ilike(search_pattern),
            )
        )

    if atc:
        stmt = stmt.where(Drug.atc_code.startswith(atc.upper().strip()))

    if therapeutic_class:
        stmt = stmt.where(Drug.therapeutic_class.ilike(f"%{therapeutic_class.strip()}%"))

    if record_status:
        stmt = stmt.where(Drug.record_status == record_status)

    if bcs_class:
        stmt = stmt.join(Drug.bcs_assessments).where(BCSAssessment.bcs_class == bcs_class).distinct()

    # Count total matching records
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = db.execute(count_stmt).scalar_one()

    # Paginate and order
    stmt = stmt.order_by(Drug.generic_name.asc()).offset(offset).limit(limit)
    drugs = db.execute(stmt).scalars().all()

    items = [DrugSummary.model_validate(d) for d in drugs]

    return Page[DrugSummary](
        items=items,
        total=total,
        offset=offset,
        limit=limit,
    )


@router.get(
    "",
    response_model=Page[DrugSummary],
    summary="List all drugs with pagination",
)
def list_drugs(
    db: DatabaseDep,
    ctx: TenantDep,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 25,
) -> Page[DrugSummary]:
    """Retrieve a paginated list of all active drugs accessible to the tenant."""
    return search_drugs(db=db, ctx=ctx, offset=offset, limit=limit)


@router.get(
    "/{drug_id_or_name}",
    response_model=DrugProfile,
    summary="Get complete drug profile by UUID or generic name",
)
def get_drug_profile(
    drug_id_or_name: str,
    db: DatabaseDep,
    ctx: TenantDep,
) -> DrugProfile:
    """Retrieve a full source-linked drug profile.

    Loads all associated data:
    - Chemical identifiers & synonyms
    - Preformulation metrics (pKa, logP, solubility, melting points)
    - BCS assessments (dose-dependent and disputed classes)
    - Dosing guidelines and maximum daily ceilings
    - Excipient compatibility matrix records
    - Indian market pharmaceutical brands & CDSCO statuses
    - Literature citations and abstract summaries
    - Active conflict logs and explicit missing data entries
    """
    stmt = (
        select(Drug)
        .options(
            selectinload(Drug.identity_source),
            selectinload(Drug.identifiers),
            selectinload(Drug.preformulation_metrics),
            selectinload(Drug.bcs_assessments),
            selectinload(Drug.dose_guidelines),
            selectinload(Drug.compatibilities),
            selectinload(Drug.indian_brands),
            selectinload(Drug.literature_links),
            selectinload(Drug.conflicts),
            selectinload(Drug.missing_data),
        )
    )

    # Check whether the identifier is a UUID or a drug generic name
    try:
        parsed_uuid = uuid.UUID(drug_id_or_name)
        stmt = stmt.where(Drug.id == parsed_uuid)
    except ValueError:
        stmt = stmt.where(func.lower(Drug.generic_name) == drug_id_or_name.strip().lower())

    drug = db.execute(stmt).scalars().first()

    if not drug:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Drug '{drug_id_or_name}' not found or not accessible within tenant context.",
        )

    return DrugProfile.model_validate(drug)
