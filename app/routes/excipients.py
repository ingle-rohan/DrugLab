"""DrugLab / DrugPedia - Excipient Library API Routes.

Implements:
- Excipient search and catalog listing with pagination
- Individual excipient profile retrieval
"""

import uuid
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import selectinload

from ..dependencies import DatabaseDep, TenantDep
from ..models import Excipient
from ..schemas import ExcipientRead, Page

router = APIRouter(prefix="/excipients", tags=["Excipients"])


@router.get(
    "",
    response_model=Page[ExcipientRead],
    summary="List and search excipients",
)
def list_excipients(
    db: DatabaseDep,
    ctx: TenantDep,
    q: Annotated[Optional[str], Query(description="Search by name, synonym, or CAS")] = None,
    function: Annotated[Optional[str], Query(description="Excipient function filter (e.g. binder, diluent)")] = None,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 25,
) -> Page[ExcipientRead]:
    """Retrieve excipients with optional filtering by name and functional role."""
    stmt = select(Excipient).options(selectinload(Excipient.source))

    if q:
        pattern = f"%{q.strip()}%"
        stmt = stmt.where(
            or_(
                Excipient.name.ilike(pattern),
                Excipient.cas_number.ilike(pattern),
                func.array_to_string(Excipient.synonyms, " ").ilike(pattern),
            )
        )

    if function:
        stmt = stmt.where(func.array_to_string(Excipient.functions, " ").ilike(f"%{function.strip()}%"))

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = db.execute(count_stmt).scalar_one()

    stmt = stmt.order_by(Excipient.name.asc()).offset(offset).limit(limit)
    records = db.execute(stmt).scalars().all()

    items = [ExcipientRead.model_validate(r) for r in records]
    return Page[ExcipientRead](
        items=items,
        total=total,
        offset=offset,
        limit=limit,
    )


@router.get(
    "/{excipient_id}",
    response_model=ExcipientRead,
    summary="Get single excipient by UUID",
)
def get_excipient(
    excipient_id: uuid.UUID,
    db: DatabaseDep,
    ctx: TenantDep,
) -> ExcipientRead:
    """Retrieve full specifications of an excipient by UUID."""
    stmt = (
        select(Excipient)
        .where(Excipient.id == excipient_id)
        .options(selectinload(Excipient.source))
    )
    exc = db.execute(stmt).scalars().first()
    if not exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Excipient ID '{excipient_id}' not found.",
        )
    return ExcipientRead.model_validate(exc)
