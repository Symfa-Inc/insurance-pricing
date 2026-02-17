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

export interface PredictResponse {
  charges: number;
  model_version?: string;
  feature_importance?: FeatureImportanceItem[];
}
