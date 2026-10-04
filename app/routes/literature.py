"""DrugLab / DrugPedia - Literature & Vector Search API Routes (Phase 3).

Implements:
- pgvector HNSW vector similarity search on literature abstracts
- Literature reference catalog and detail endpoints
- Admin embedding generation trigger
"""

import uuid
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import selectinload

from ..dependencies import DatabaseDep, TenantDep
from ..models import DrugLiterature, EvidenceLevel, LiteratureReference
from ..schemas import (
    LiteratureHit,
    LiteratureRead,
    LiteratureSimilaritySearchRequest,
    Page,
)
from ..services.embedding import update_all_literature_embeddings
from ..services.rag import search_literature_vector

router = APIRouter(prefix="/literature", tags=["Literature & Vector Search"])


@router.post(
    "/search",
    response_model=list[LiteratureHit],
    summary="Vector similarity search across scientific literature via pgvector",
)
def search_literature(
    payload: LiteratureSimilaritySearchRequest,
    db: DatabaseDep,
    ctx: TenantDep,
) -> list[LiteratureHit]:
    """Execute 1536-dimensional dense vector similarity search using pgvector HNSW index.

    Returns ranked literature hits with cosine similarities, original-wording abstract
    summaries, DOI links, and Evidence Level markers (A-E).
    """
    return search_literature_vector(
        session=db,
        query_text=payload.query,
        top_k=payload.top_k,
        min_evidence_level=payload.min_evidence_level,
        drug_id=payload.drug_id,
    )


@router.get(
    "",
    response_model=Page[LiteratureRead],
    summary="List literature references with filtering and pagination",
)
def list_literature(
    db: DatabaseDep,
    ctx: TenantDep,
    q: Annotated[Optional[str], Query(description="Search title, authors, or journal")] = None,
    drug_id: Annotated[Optional[uuid.UUID], Query(description="Filter by linked drug UUID")] = None,
    evidence_level: Annotated[Optional[EvidenceLevel], Query(description="Filter by Evidence Level")] = None,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 25,
) -> Page[LiteratureRead]:
    """Retrieve catalog of literature references."""
    stmt = select(LiteratureReference).options(selectinload(LiteratureReference.source))

    if q:
        pattern = f"%{q.strip()}%"
        stmt = stmt.where(
            or_(
                LiteratureReference.title.ilike(pattern),
                LiteratureReference.journal.ilike(pattern),
                LiteratureReference.abstract_summary.ilike(pattern),
                func.array_to_string(LiteratureReference.authors, " ").ilike(pattern),
            )
        )

    if evidence_level:
        stmt = stmt.where(LiteratureReference.evidence_level == evidence_level)

    if drug_id:
        stmt = stmt.join(DrugLiterature, DrugLiterature.literature_id == LiteratureReference.id).where(
            DrugLiterature.drug_id == drug_id
        )

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = db.execute(count_stmt).scalar_one()

    stmt = stmt.order_by(LiteratureReference.publication_year.desc().nullslast()).offset(offset).limit(limit)
    records = db.execute(stmt).scalars().all()

    items = [LiteratureRead.model_validate(r) for r in records]
    return Page[LiteratureRead](
        items=items,
        total=total,
        offset=offset,
        limit=limit,
    )


@router.get(
    "/{literature_id}",
    response_model=LiteratureRead,
    summary="Get single literature reference by UUID",
)
def get_literature_detail(
    literature_id: uuid.UUID,
    db: DatabaseDep,
    ctx: TenantDep,
) -> LiteratureRead:
    """Retrieve complete metadata of a literature reference by its UUID."""
    stmt = (
        select(LiteratureReference)
        .where(LiteratureReference.id == literature_id)
        .options(selectinload(LiteratureReference.source))
    )
    ref = db.execute(stmt).scalars().first()
    if not ref:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Literature reference '{literature_id}' not found.",
        )
    return LiteratureRead.model_validate(ref)


@router.post(
    "/embed-all",
    summary="Batch generate and update embeddings for all literature references",
)
def trigger_embedding_update(
    db: DatabaseDep,
    ctx: TenantDep,
    force: bool = False,
):
    """Platform maintenance endpoint to ensure all literature records carry vector embeddings."""
    count = update_all_literature_embeddings(session=db, force=force)
    return {
        "status": "success",
        "records_embedded": count,
        "message": f"Successfully updated {count} literature embeddings in pgvector.",
    }
