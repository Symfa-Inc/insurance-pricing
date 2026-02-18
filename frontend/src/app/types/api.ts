export type Sex = "female" | "male";
export type Smoker = "no" | "yes";
export type Region = "northeast" | "northwest" | "southeast" | "southwest";

export interface PredictRequest {
  age: number;
  sex: Sex;
  bmi: number;
  children: number;
  smoker: Smoker;
  region: Region;
}

export interface FeatureImportanceItem {
  name: string;
  value: number;
}

export interface ShapContribution {
  feature: string;
  value: string | number;
  shap_value: number;
  abs_shap_value: number;
}

export interface ShapPayload {
  base_value: number;
  contributions: ShapContribution[];
  top_k: number;
}

export interface InterpretationTopFeature {
  feature: string;
  direction: "increases" | "decreases" | "mixed";
  strength: "high" | "medium" | "low";
}

export interface InterpretationPayload {
  headline: string;
  bullets: string[];
  caveats: string[];
  top_features: InterpretationTopFeature[];
}

export interface PredictResponse {
  charges: number;
  model_version?: string;
  extrapolation_warnings?: string[];
  shap?: ShapPayload;
  interpretation?: InterpretationPayload;
  explainability_error?: string | null;
  llm_error?: string | null;
  feature_importance?: FeatureImportanceItem[];
}
