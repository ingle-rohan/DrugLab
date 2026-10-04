"""DrugLab / DrugPedia - Drug-Excipient Compatibility Engine API Routes.

Implements:
- Direct compatibility checks by drug and excipient IDs
- Derived verdict computation following pharmaceutical evidence hierarchies
- Batch compatibility profile for a drug across all studied excipients
"""

import uuid
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from ..dependencies import DatabaseDep, TenantDep
from ..models import (
    CompatibilityCategory,
    Drug,
    DrugExcipientCompatibility,
    Excipient,
)
from ..schemas import (
    CompatibilityCheckRequest,
    CompatibilityCheckResponse,
    CompatibilityRead,
    ExcipientSummary,
)

router = APIRouter(prefix="/compatibility", tags=["Compatibility Engine"])


def _calculate_verdict(evidence: list[CompatibilityRead]) -> CompatibilityCategory:
    """Calculate the derived compatibility verdict across multiple evidence rows.

    Precedence:
    1. INCOMPATIBLE_UNDER_CONDITIONS: Direct documented physical/chemical degradation
    2. POTENTIAL_INTERACTION: Interaction noted (e.g. eutectic, Maillard, moisture catalysis)
    3. COMPATIBLE_UNDER_CONDITIONS: Verified compatible under studied formulation conditions
    4. INSUFFICIENT_EVIDENCE: No studies or inconclusive evidence
    """
    if not evidence:
        return CompatibilityCategory.INSUFFICIENT_EVIDENCE

    categories = {e.category for e in evidence}

    if CompatibilityCategory.INCOMPATIBLE_UNDER_CONDITIONS in categories:
        return CompatibilityCategory.INCOMPATIBLE_UNDER_CONDITIONS
    if CompatibilityCategory.POTENTIAL_INTERACTION in categories:
        return CompatibilityCategory.POTENTIAL_INTERACTION
    if CompatibilityCategory.COMPATIBLE_UNDER_CONDITIONS in categories:
        return CompatibilityCategory.COMPATIBLE_UNDER_CONDITIONS

    return CompatibilityCategory.INSUFFICIENT_EVIDENCE


@router.get(
    "/check",
    response_model=CompatibilityCheckResponse,
    summary="Evaluate compatibility between a drug and excipient",
)
def check_compatibility(
    db: DatabaseDep,
    ctx: TenantDep,
    drug_id: Annotated[uuid.UUID, Query(description="Drug UUID")],
    excipient_id: Annotated[uuid.UUID, Query(description="Excipient UUID")],
) -> CompatibilityCheckResponse:
    """Perform a condition-specific compatibility check between an API and an excipient.

    Emits source citations, testing methods (FTIR, DSC, XRD), environmental conditions,
    and a formal pharmaceutical disclaimer.
    """
    # Verify existence of drug
    drug = db.get(Drug, drug_id)
    if not drug:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Drug ID '{drug_id}' not found.",
        )

    # Verify existence of excipient
    excipient = db.get(Excipient, excipient_id)
    if not excipient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Excipient ID '{excipient_id}' not found.",
        )

    stmt = (
        select(DrugExcipientCompatibility)
        .where(
            DrugExcipientCompatibility.drug_id == drug_id,
            DrugExcipientCompatibility.excipient_id == excipient_id,
        )
    )
    records = db.execute(stmt).scalars().all()

    evidence_items = [CompatibilityRead.model_validate(r) for r in records]
    verdict = _calculate_verdict(evidence_items)

    return CompatibilityCheckResponse(
        drug_id=drug_id,
        excipient_id=excipient_id,
        verdict=verdict,
        evidence=evidence_items,
        disclaimer=(
            "Results are specific to the listed conditions. 'No evidence of interaction' is not proof of universal compatibility. "
            "Formulation stability testing (ICH Q1A) is mandatory for regulatory filing."
        ),
    )


@router.post(
    "/check",
    response_model=CompatibilityCheckResponse,
    summary="Evaluate compatibility via JSON payload",
)
def check_compatibility_post(
    payload: CompatibilityCheckRequest,
    db: DatabaseDep,
    ctx: TenantDep,
) -> CompatibilityCheckResponse:
    """POST endpoint for checking compatibility using a structured JSON body."""
    return check_compatibility(
        db=db,
        ctx=ctx,
        drug_id=payload.drug_id,
        excipient_id=payload.excipient_id,
    )


@router.get(
    "/matrix/{drug_id}",
    response_model=list[CompatibilityRead],
    summary="Get all studied excipient compatibility records for a drug",
)
def get_drug_compatibility_matrix(
    drug_id: uuid.UUID,
    db: DatabaseDep,
    ctx: TenantDep,
) -> list[CompatibilityRead]:
    """Retrieve all excipient interaction studies associated with a specific drug."""
    drug = db.get(Drug, drug_id)
    if not drug:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Drug ID '{drug_id}' not found.",
        )

    stmt = (
        select(DrugExcipientCompatibility)
        .where(DrugExcipientCompatibility.drug_id == drug_id)
        .order_by(DrugExcipientCompatibility.category.asc())
    )
    records = db.execute(stmt).scalars().all()
    return [CompatibilityRead.model_validate(r) for r in records]
