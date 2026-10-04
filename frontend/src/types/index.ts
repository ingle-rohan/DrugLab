export type EvidenceLevel = "A" | "B" | "C" | "D" | "E";

export type CompatibilityCategory =
  | "compatible_under_conditions"
  | "potential_interaction"
  | "incompatible_under_conditions"
  | "insufficient_evidence";

export type ConfidenceLevel = "low" | "medium" | "high";

export interface SourceBrief {
  id: string;
  name: string;
  url?: string;
  doi?: string;
  pmid?: string;
  source_type: string;
  publication_date?: string;
}

export interface DrugSummary {
  id: string;
  generic_name: string;
  form_tag: string;
  inn?: string;
  therapeutic_class?: string;
  atc_code?: string;
  cas_number?: string;
  molecular_formula?: string;
  molecular_weight?: number;
  record_status: string;
  identity_evidence_level?: EvidenceLevel;
}

export interface PreformulationMetric {
  id: string;
  metric_type: string;
  metric_label?: string;
  value_numeric?: number;
  value_min?: number;
  value_max?: number;
  value_text?: string;
  unit?: string;
  origin: string;
  temperature_c?: number;
  ph?: number;
  medium?: string;
  method?: string;
  solid_form?: string;
  ionizable_group?: string;
  pka_ordinal?: number;
  conflict_flag: boolean;
  notes?: string;
  evidence_level: EvidenceLevel;
  source: SourceBrief;
  source_locator?: string;
}

export interface BCSAssessment {
  id: string;
  bcs_class?: string;
  framework?: string;
  dose_mg_min?: number;
  dose_mg_max?: number;
  solubility_basis?: string;
  permeability_basis?: string;
  is_disputed: boolean;
  is_regulatory_classification: boolean;
  rationale?: string;
  evidence_level: EvidenceLevel;
  source: SourceBrief;
}

export interface DoseGuideline {
  id: string;
  population: string;
  route: string;
  indication?: string;
  regimen_text: string;
  dose_mg_min?: number;
  dose_mg_max?: number;
  interval_hours?: number;
  max_daily_dose_mg?: number;
  max_daily_dose_period_hours?: number;
  jurisdiction: string;
  evidence_level: EvidenceLevel;
  source: SourceBrief;
}

export interface ExcipientSummary {
  id: string;
  name: string;
  functions: string[];
}

export interface CompatibilityItem {
  id: string;
  drug_id: string;
  excipient_id: string;
  excipient: ExcipientSummary;
  category: CompatibilityCategory;
  category_code: number;
  reported_interaction?: string;
  possible_mechanism?: string;
  methods: string[];
  temperature_c?: number;
  relative_humidity_pct?: number;
  duration_text?: string;
  conditions_summary?: string;
  evidence_level: EvidenceLevel;
  source: SourceBrief;
}

export interface IndianBrand {
  id: string;
  brand_name: string;
  manufacturer?: string;
  strength?: string;
  dosage_form?: string;
  route?: string;
  pack_size?: string;
  ip_labelled?: boolean;
  verification_status: string;
  manufacturer_conflict: boolean;
  conflicting_manufacturers: string[];
  cdsco_approval_ref?: string;
  mrp_inr?: number;
  evidence_level: EvidenceLevel;
}

export interface ConflictLogItem {
  id: string;
  field_name: string;
  claim: string;
  difference?: string;
  possible_reason?: string;
  current_interpretation?: string;
  confidence: ConfidenceLevel;
  resolved: boolean;
  source_1?: SourceBrief;
  source_2?: SourceBrief;
}

export interface MissingDataItem {
  id: string;
  field_name: string;
  statement: string;
  suggested_next_step?: string;
  searched_on?: string;
  is_resolved: boolean;
}

export interface DrugProfile extends DrugSummary {
  form_description?: string;
  usan?: string;
  ban?: string;
  us_name?: string;
  synonyms: string[];
  pharmacological_class?: string;
  chemical_class?: string;
  unii?: string;
  pubchem_cid?: number;
  iupac_name?: string;
  exact_mass?: number;
  smiles_isomeric?: string;
  smiles_canonical?: string;
  inchi?: string;
  inchikey?: string;
  stereocentre_count?: number;
  stereochemistry_note?: string;
  functional_groups: string[];
  mechanism_of_action?: string;
  pharmacological_action?: string;
  scope_note?: string;
  open_conflict_count: number;
  preformulation_metrics: PreformulationMetric[];
  bcs_assessments: BCSAssessment[];
  dose_guidelines: DoseGuideline[];
  compatibilities: CompatibilityItem[];
  indian_brands: IndianBrand[];
  conflicts: ConflictLogItem[];
  missing_data: MissingDataItem[];
}

export interface ExcipientRead {
  id: string;
  name: string;
  synonyms: string[];
  cas_number?: string;
  functions: string[];
  common_dosage_forms: string[];
  applications?: string;
  typical_conc_min_pct?: number;
  typical_conc_max_pct?: number;
  typical_conc_basis?: string;
  physicochemical: Record<string, any>;
  pharmacopoeial_status: Record<string, any>;
  evidence_level: EvidenceLevel;
  source: SourceBrief;
}

export interface CompatibilityCheckResponse {
  drug_id: string;
  excipient_id: string;
  verdict: CompatibilityCategory;
  evidence: CompatibilityItem[];
  disclaimer: string;
}

export interface ProvenanceClaim {
  statement: string;
  source_name: string;
  source_locator?: string;
  source_url?: string;
  evidence_level: EvidenceLevel;
  evidence_label: string;
  confidence: ConfidenceLevel;
  conditions?: Record<string, any>;
  dispute_flag: boolean;
}

export interface LiteratureHit {
  reference: {
    id: string;
    title: string;
    authors: string[];
    journal?: string;
    publication_year?: number;
    study_type?: string;
    doi?: string;
    pmid?: string;
    url?: string;
    abstract_summary?: string;
    evidence_level: EvidenceLevel;
    evidence_label: string;
  };
  cosine_similarity: number;
}

export interface RAGResponse {
  query: string;
  answer_markdown: string;
  claims: ProvenanceClaim[];
  literature_citations: LiteratureHit[];
  relational_entities_cited: string[];
  confidence: ConfidenceLevel;
  disclaimer: string;
}
