"""DrugLab / DrugPedia - RAG Provenance Engine API Routes (Phase 3).

Exposes the Retrieval-Augmented Generation (RAG) engine backed by strict data provenance tracking.
Every AI response field dynamically emits source links and Evidence Level indicators (A-E).
"""

import uuid
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Query

from ..dependencies import DatabaseDep, TenantDep
from ..models import EvidenceLevel
from ..schemas import RAGQueryRequest, RAGResponse
from ..services.rag import execute_rag_query

router = APIRouter(prefix="/rag", tags=["RAG Provenance Engine"])


@router.post(
    "/query",
    response_model=RAGResponse,
    summary="Query the pharmaceutical RAG intelligence engine with provenance citations",
)
def rag_query_endpoint(
    payload: RAGQueryRequest,
    db: DatabaseDep,
    ctx: TenantDep,
) -> RAGResponse:
    """Execute evidence-backed question answering across the DrugLab knowledge base.

    The engine:
    1. Extracts API and excipient entities from the prompt
    2. Performs pgvector dense similarity search across scientific literature
    3. Retrieves relational facts (preformulation, BCS, dosing, compatibility)
    4. Dynamically binds every response claim to an authoritative source and Evidence Level (A-E)
    """
    return execute_rag_query(
        session=db,
        query=payload.query,
        drug_id=payload.drug_id,
        top_k_literature=payload.top_k_literature,
        min_evidence_level=payload.min_evidence_level,
    )


@router.get(
    "/query",
    response_model=RAGResponse,
    summary="GET endpoint for quick natural language RAG queries",
)
def rag_query_get_endpoint(
    db: DatabaseDep,
    ctx: TenantDep,
    q: Annotated[str, Query(min_length=3, description="Pharmaceutical question or formulation prompt")],
    drug_id: Annotated[Optional[uuid.UUID], Query(description="Target drug UUID (optional)")] = None,
    top_k: Annotated[int, Query(ge=1, le=20, description="Max literature citations")] = 5,
    min_evidence_level: Annotated[EvidenceLevel, Query(description="Minimum evidence tier")] = EvidenceLevel.E,
) -> RAGResponse:
    """Convenience GET endpoint for the RAG engine."""
    return execute_rag_query(
        session=db,
        query=q,
        drug_id=drug_id,
        top_k_literature=top_k,
        min_evidence_level=min_evidence_level,
    )
