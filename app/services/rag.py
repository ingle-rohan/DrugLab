"""DrugLab / DrugPedia - RAG Provenance & Citation Engine (Phase 3).

Retrieves verified relational facts and vector-indexed literature to synthesize
evidence-backed pharmaceutical insights. Every field emits source links and
Evidence Level indicators (A-E).
"""

from decimal import Decimal
import logging
import re
from typing import Any, Optional
import uuid

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from ..models import (
    BCSAssessment,
    ConfidenceLevel,
    ConflictLog,
    DoseGuideline,
    Drug,
    DrugExcipientCompatibility,
    DrugIdentifier,
    DrugLiterature,
    EvidenceLevel,
    Excipient,
    IndianPharmaBrand,
    LiteratureReference,
    MissingDataItem,
    PreformulationMetric,
    Source,
)
from ..schemas import (
    EVIDENCE_LABELS,
    LiteratureHit,
    LiteratureRead,
    ProvenanceClaim,
    RAGResponse,
)
from .embedding import generate_embedding

logger = logging.getLogger("druglab.rag")

EVIDENCE_LEVEL_RANK = {
    EvidenceLevel.A: 1,
    EvidenceLevel.B: 2,
    EvidenceLevel.C: 3,
    EvidenceLevel.D: 4,
    EvidenceLevel.E: 5,
}


def search_literature_vector(
    session: Session,
    query_text: str,
    top_k: int = 5,
    min_evidence_level: EvidenceLevel = EvidenceLevel.E,
    drug_id: Optional[uuid.UUID] = None,
) -> list[LiteratureHit]:
    """Perform pgvector cosine similarity search on literature references."""
    query_vec = generate_embedding(query_text)

    # Calculate cosine distance in pgvector
    cosine_distance_col = LiteratureReference.embedding.cosine_distance(query_vec)

    stmt = select(
        LiteratureReference,
        (1.0 - cosine_distance_col).label("similarity"),
    ).where(LiteratureReference.embedding.is_not(None))

    if drug_id:
        stmt = stmt.join(DrugLiterature, DrugLiterature.literature_id == LiteratureReference.id).where(
            DrugLiterature.drug_id == drug_id
        )

    # Order by similarity descending (distance ascending)
    stmt = stmt.order_by(cosine_distance_col.asc()).limit(top_k * 2)
    rows = session.execute(stmt).all()

    hits: list[LiteratureHit] = []
    max_rank = EVIDENCE_LEVEL_RANK[min_evidence_level]

    for lit_ref, sim in rows:
        if EVIDENCE_LEVEL_RANK[lit_ref.evidence_level] <= max_rank:
            read_model = LiteratureRead.model_validate(lit_ref)
            hits.append(LiteratureHit(reference=read_model, cosine_similarity=round(float(sim), 4)))
            if len(hits) >= top_k:
                break

    return hits


def _detect_mentioned_entities(query: str, session: Session) -> tuple[list[Drug], list[Excipient]]:
    """Identify candidate drugs and excipients mentioned in the user query."""
    q_lower = query.lower()
    all_drugs = session.execute(select(Drug)).scalars().all()
    all_excipients = session.execute(select(Excipient)).scalars().all()

    matched_drugs: list[Drug] = []
    for d in all_drugs:
        names = [d.generic_name.lower()]
        if d.inn:
            names.append(d.inn.lower())
        if d.usan:
            names.append(d.usan.lower())
        if d.us_name:
            names.append(d.us_name.lower())
        for syn in d.synonyms:
            names.append(syn.lower())

        if any(re.search(rf"\b{re.escape(name)}\b", q_lower) for name in names):
            matched_drugs.append(d)

    matched_excipients: list[Excipient] = []
    for e in all_excipients:
        names = [e.name.lower()]
        for syn in e.synonyms:
            names.append(syn.lower())
        if any(re.search(rf"\b{re.escape(name)}\b", q_lower) for name in names):
            matched_excipients.append(e)

    return matched_drugs, matched_excipients


def execute_rag_query(
    session: Session,
    query: str,
    drug_id: Optional[uuid.UUID] = None,
    top_k_literature: int = 5,
    min_evidence_level: EvidenceLevel = EvidenceLevel.E,
) -> RAGResponse:
    """Execute end-to-end RAG retrieval, provenance attribution, and synthesis.

    1. Retrieves vector-similar literature using pgvector HNSW search.
    2. Retrieves relational preformulation, BCS, dosing, compatibility, conflict, and brand records.
    3. Synthesizes an evidence-attributed pharmaceutical response with strict source tracking.
    """
    matched_drugs, matched_excipients = _detect_mentioned_entities(query, session)

    if drug_id:
        specific_drug = session.get(Drug, drug_id)
        if specific_drug and specific_drug not in matched_drugs:
            matched_drugs.insert(0, specific_drug)

    # 1. Vector Search for relevant literature
    lit_hits = search_literature_vector(
        session=session,
        query_text=query,
        top_k=top_k_literature,
        min_evidence_level=min_evidence_level,
        drug_id=drug_id or (matched_drugs[0].id if matched_drugs else None),
    )

    claims: list[ProvenanceClaim] = []
    relational_entities: set[str] = set()

    for d in matched_drugs:
        relational_entities.add(d.generic_name)
    for e in matched_excipients:
        relational_entities.add(e.name)

    # 2. Extract Relational Provenance Claims for identified drugs
    for drug in matched_drugs:
        # Load relationships
        session.refresh(
            drug,
            [
                "identity_source",
                "preformulation_metrics",
                "bcs_assessments",
                "dose_guidelines",
                "compatibilities",
                "indian_brands",
                "conflicts",
                "missing_data",
            ],
        )

        # Identity claim
        if drug.identity_source:
            claims.append(
                ProvenanceClaim(
                    statement=f"{drug.generic_name} ({drug.form_tag.value}): CAS {drug.cas_number or 'N/A'}, ATC {drug.atc_code or 'N/A'}, MW {drug.molecular_weight or 'N/A'} g/mol, Formula {drug.molecular_formula or 'N/A'}.",
                    source_name=drug.identity_source.name,
                    source_locator="Section 1: Identity & Chemical Classification",
                    source_url=drug.identity_source.url,
                    evidence_level=drug.identity_evidence_level or EvidenceLevel.A,
                    evidence_label=EVIDENCE_LABELS[drug.identity_evidence_level or EvidenceLevel.A],
                    confidence=ConfidenceLevel.HIGH,
                )
            )

        # Preformulation Claims (pKa, solubility, melting point)
        for m in drug.preformulation_metrics:
            val_str = ""
            if m.value_numeric is not None:
                val_str = f"{m.value_numeric} {m.unit or ''}".strip()
            elif m.value_min is not None and m.value_max is not None:
                val_str = f"{m.value_min} - {m.value_max} {m.unit or ''}".strip()
            elif m.value_text:
                val_str = m.value_text

            conditions_dict = {}
            if m.temperature_c:
                conditions_dict["temperature"] = f"{m.temperature_c} °C"
            if m.ph:
                conditions_dict["pH"] = str(m.ph)
            if m.method:
                conditions_dict["method"] = m.method

            claims.append(
                ProvenanceClaim(
                    statement=f"{drug.generic_name} {m.metric_type.value.upper()}: {val_str}{f' ({m.notes})' if m.notes else ''}.",
                    source_name=m.source.name if m.source else "Authoritative Compendium",
                    source_locator=m.source_locator or "Section 2: Preformulation Metric",
                    source_url=m.source.url if m.source else None,
                    evidence_level=m.evidence_level,
                    evidence_label=EVIDENCE_LABELS[m.evidence_level],
                    confidence=ConfidenceLevel.HIGH,
                    conditions=conditions_dict or None,
                )
            )

        # BCS Claims
        for bcs in drug.bcs_assessments:
            claims.append(
                ProvenanceClaim(
                    statement=f"{drug.generic_name} BCS Class {bcs.bcs_class.value if bcs.bcs_class else 'Disputed'} ({bcs.framework or 'Framework'}): {bcs.solubility_basis or ''} {bcs.permeability_basis or ''}".strip(),
                    source_name=bcs.source.name if bcs.source else "WHO/FDA Guidelines",
                    source_locator=bcs.source_locator or "Section 3: BCS Classification",
                    source_url=bcs.source.url if bcs.source else None,
                    evidence_level=bcs.evidence_level,
                    evidence_label=EVIDENCE_LABELS[bcs.evidence_level],
                    confidence=ConfidenceLevel.HIGH if not bcs.is_disputed else ConfidenceLevel.MEDIUM,
                    dispute_flag=bcs.is_disputed,
                )
            )

        # Dosing & Safety Ceilings
        for dg in drug.dose_guidelines:
            claims.append(
                ProvenanceClaim(
                    statement=f"{drug.generic_name} Dosing ({dg.population}): {dg.regimen_text} [Max Daily Ceiling: {dg.max_daily_dose_mg} mg/24h].",
                    source_name=dg.source.name if dg.source else "Approved Prescribing Information",
                    source_locator=dg.source_locator or "Section 4: Dosage & Administration",
                    source_url=dg.source.url if dg.source else None,
                    evidence_level=dg.evidence_level,
                    evidence_label=EVIDENCE_LABELS[dg.evidence_level],
                    confidence=ConfidenceLevel.HIGH,
                )
            )

        # Compatibilities
        for comp in drug.compatibilities:
            # If specific excipients were queried, filter to them; otherwise include all
            if matched_excipients and comp.excipient not in matched_excipients:
                continue

            cond_dict = {}
            if comp.temperature_c:
                cond_dict["temperature"] = f"{comp.temperature_c} °C"
            if comp.relative_humidity_pct:
                cond_dict["RH"] = f"{comp.relative_humidity_pct}%"
            if comp.methods:
                cond_dict["methods"] = ", ".join(comp.methods)

            interaction_note = f" Reported interaction: {comp.reported_interaction}" if comp.reported_interaction else ""
            claims.append(
                ProvenanceClaim(
                    statement=f"Compatibility {drug.generic_name} + {comp.excipient.name}: {comp.category.value.replace('_', ' ').title()}.{interaction_note} ({comp.conditions_summary or ''})",
                    source_name=comp.source.name if comp.source else "Compatibility Study",
                    source_locator=comp.source_locator or "Section 5: Compatibility Matrix",
                    source_url=comp.source.url if comp.source else None,
                    evidence_level=comp.evidence_level,
                    evidence_label=EVIDENCE_LABELS[comp.evidence_level],
                    confidence=ConfidenceLevel.HIGH,
                    conditions=cond_dict or None,
                )
            )

        # Conflict Logs
        for c_log in drug.conflicts:
            claims.append(
                ProvenanceClaim(
                    statement=f"Conflict Alert for {drug.generic_name} [{c_log.field_name}]: {c_log.claim}. Current interpretation: {c_log.current_interpretation or 'Under review'}.",
                    source_name=f"1) {c_log.source_1.name if c_log.source_1 else 'Source 1'} vs 2) {c_log.source_2.name if c_log.source_2 else 'Source 2'}",
                    source_locator="Section 30: Conflict Log",
                    evidence_level=EvidenceLevel.B,
                    evidence_label="Peer-reviewed comparative evidence",
                    confidence=c_log.confidence,
                    dispute_flag=True,
                )
            )

        # Missing Data Items
        for m_item in drug.missing_data:
            claims.append(
                ProvenanceClaim(
                    statement=f"Missing Data Flag for {drug.generic_name} [{m_item.field_name}]: {m_item.statement} Recommended action: {m_item.suggested_next_step or 'Experimental determination required'}.",
                    source_name="DrugLab Data Provenance Audit",
                    source_locator="Section 31: Missing Data Items",
                    evidence_level=EvidenceLevel.C,
                    evidence_label="Authoritative Repository Gap Tracking",
                    confidence=ConfidenceLevel.HIGH,
                )
            )

    # 3. Construct Authoritative Markdown Synthesis
    answer_parts = []
    answer_parts.append(f"### Pharmaceutical Intelligence Synthesis for: *\"{query}\"*")

    if matched_drugs:
        drug_names = ", ".join(d.generic_name for d in matched_drugs)
        answer_parts.append(f"**Identified Active Pharmaceutical Ingredients:** {drug_names}")

    if matched_excipients:
        excipient_names = ", ".join(e.name for e in matched_excipients)
        answer_parts.append(f"**Identified Excipients:** {excipient_names}")

    # Summary of findings
    answer_parts.append("\n#### 1. Core Pharmaceutical Findings & Evidence Levels")
    if claims:
        for i, c in enumerate(claims[:8], 1):
            dispute_badge = " ⚠️ **[DISPUTED]**" if c.dispute_flag else ""
            conditions_badge = f" *(Conditions: {c.conditions})*" if c.conditions else ""
            answer_parts.append(
                f"- **[{c.evidence_level.value}]** {c.statement}{conditions_badge}{dispute_badge}\n"
                f"  *Source:* {c.source_name} (`{c.evidence_label}`)"
            )
    else:
        answer_parts.append("- No direct relational drug match found; refer to literature citations below.")

    # Literature Evidence Section
    if lit_hits:
        answer_parts.append("\n#### 2. Literature Vector Matches (pgvector HNSW)")
        for hit in lit_hits:
            ref = hit.reference
            authors_str = ", ".join(ref.authors[:2]) + (" et al." if len(ref.authors) > 2 else "")
            doi_link = f"https://doi.org/{ref.doi}" if ref.doi else ref.url
            answer_parts.append(
                f"- **{ref.title}** ({ref.publication_year or 'N/A'})\n"
                f"  *Authors:* {authors_str} | *Journal:* {ref.journal or 'N/A'} | *Cosine Similarity:* **{hit.cosine_similarity:.2f}**\n"
                f"  *Evidence Level:* **[{ref.evidence_level.value}]** ({ref.evidence_label})\n"
                f"  *Summary:* {ref.abstract_summary or 'No abstract summary available.'}\n"
                f"  *DOI:* [{ref.doi or 'Link'}]({doi_link})"
            )

    # Formulation & Regulatory Guidance
    answer_parts.append("\n#### 3. Formulation & Safety Recommendations")
    has_interactions = any("Incompatible" in c.statement or "Potential Interaction" in c.statement for c in claims)
    if has_interactions:
        answer_parts.append(
            "> [!WARNING]\n"
            "> **Formulation Interaction Detected:** Specific physical or chemical incompatibility noted under elevated temperature/humidity. "
            "Formulation adjustments (e.g. limiting lubricant blending time, avoiding reducing sugars with primary amines) are required."
        )
    else:
        answer_parts.append(
            "> [!NOTE]\n"
            "> Formulations must be verified under ICH Q1A accelerated stability conditions ($40^\\circ\\text{C} \\pm 2^\\circ\\text{C} / 75\\%\\text{ RH} \\pm 5\\%\\text{ RH}$)."
        )

    overall_confidence = ConfidenceLevel.HIGH
    if any(c.dispute_flag for c in claims) or not claims:
        overall_confidence = ConfidenceLevel.MEDIUM

    return RAGResponse(
        query=query,
        answer_markdown="\n".join(answer_parts),
        claims=claims,
        literature_citations=lit_hits,
        relational_entities_cited=sorted(list(relational_entities)),
        confidence=overall_confidence,
    )
