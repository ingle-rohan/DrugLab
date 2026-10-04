import {
  DrugSummary,
  DrugProfile,
  ExcipientRead,
  CompatibilityCheckResponse,
  CompatibilityItem,
  RAGResponse,
  LiteratureHit,
} from "../types";

const API_BASE = "/api/v1";

export async function searchDrugs(
  q?: string,
  atc?: string,
  bcs?: string,
  offset = 0,
  limit = 25
): Promise<{ items: DrugSummary[]; total: number }> {
  const params = new URLSearchParams();
  if (q) params.set("q", q);
  if (atc) params.set("atc", atc);
  if (bcs) params.set("bcs_class", bcs);
  params.set("offset", offset.toString());
  params.set("limit", limit.toString());

  const res = await fetch(`${API_BASE}/drugs/search?${params.toString()}`);
  if (!res.ok) throw new Error("Failed to search drugs");
  return res.json();
}

export async function getDrugProfile(idOrName: string): Promise<DrugProfile> {
  const res = await fetch(`${API_BASE}/drugs/${encodeURIComponent(idOrName)}`);
  if (!res.ok) throw new Error(`Drug profile not found for ${idOrName}`);
  return res.json();
}

export async function listExcipients(
  q?: string,
  func?: string,
  offset = 0,
  limit = 25
): Promise<{ items: ExcipientRead[]; total: number }> {
  const params = new URLSearchParams();
  if (q) params.set("q", q);
  if (func) params.set("function", func);
  params.set("offset", offset.toString());
  params.set("limit", limit.toString());

  const res = await fetch(`${API_BASE}/excipients?${params.toString()}`);
  if (!res.ok) throw new Error("Failed to fetch excipients");
  return res.json();
}

export async function getExcipient(id: string): Promise<ExcipientRead> {
  const res = await fetch(`${API_BASE}/excipients/${id}`);
  if (!res.ok) throw new Error(`Excipient not found for ${id}`);
  return res.json();
}

export async function checkCompatibility(
  drugId: string,
  excipientId: string
): Promise<CompatibilityCheckResponse> {
  const res = await fetch(`${API_BASE}/compatibility/check`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ drug_id: drugId, excipient_id: excipientId }),
  });
  if (!res.ok) throw new Error("Failed to evaluate compatibility");
  return res.json();
}

export async function getDrugCompatibilityMatrix(
  drugId: string
): Promise<CompatibilityItem[]> {
  const res = await fetch(`${API_BASE}/compatibility/matrix/${drugId}`);
  if (!res.ok) throw new Error("Failed to fetch compatibility matrix");
  return res.json();
}

export async function queryRAG(
  query: string,
  drugId?: string
): Promise<RAGResponse> {
  const res = await fetch(`${API_BASE}/rag/query`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      query,
      drug_id: drugId,
      top_k_literature: 4,
    }),
  });
  if (!res.ok) throw new Error("RAG query failed");
  return res.json();
}

export async function searchLiterature(
  query: string,
  topK = 5
): Promise<LiteratureHit[]> {
  const res = await fetch(`${API_BASE}/literature/search`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query, top_k: topK }),
  });
  if (!res.ok) throw new Error("Literature vector search failed");
  return res.json();
}
