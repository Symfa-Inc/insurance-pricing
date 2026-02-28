import type { PredictRequest, Region, Sex, Smoker } from "@/app/types/api";

export type FeatureId = keyof PredictRequest;
export type FeatureFormValues = Record<FeatureId, string>;

interface BaseFeatureSchema<I extends FeatureId, K extends "number" | "select"> {
  id: I;
  type: K;
  label: string;
}

export interface NumericFeatureSchema<I extends FeatureId = FeatureId>
  extends BaseFeatureSchema<I, "number"> {
  defaultValue: number;
  placeholder?: string;
  help?: string;
  step?: number;
}

export interface SelectFeatureSchema<I extends FeatureId = FeatureId, O extends string = string>
  extends BaseFeatureSchema<I, "select"> {
  options: readonly O[];
  defaultValue: O;
}

export type FeatureSchema = NumericFeatureSchema | SelectFeatureSchema;

const SEX_OPTIONS = ["female", "male"] as const satisfies readonly Sex[];
const SMOKER_OPTIONS = ["no", "yes"] as const satisfies readonly Smoker[];
const REGION_OPTIONS = ["northeast", "northwest", "southeast", "southwest"] as const satisfies readonly Region[];

export const FEATURE_SCHEMA: readonly FeatureSchema[] = [
  {
    id: "age",
    type: "number",
    label: "Age",
    defaultValue: 35,
    placeholder: "e.g. 42",
    help: "Age in years",
  },
  {
    id: "sex",
    type: "select",
    label: "Sex",
    options: SEX_OPTIONS,
    defaultValue: "female",
  },
  {
    id: "bmi",
    type: "number",
    label: "BMI",
    defaultValue: 27.5,
    placeholder: "e.g. 24.3",
    help: "Body mass index",
    step: 0.5,
  },
  {
    id: "children",
    type: "number",
    label: "Children",
    defaultValue: 0,
    placeholder: "e.g. 2",
    help: "Number of dependents",
  },
  {
    id: "smoker",
    type: "select",
    label: "Smoker",
    options: SMOKER_OPTIONS,
    defaultValue: "no",
  },
  {
    id: "region",
    type: "select",
    label: "Region",
    options: REGION_OPTIONS,
    defaultValue: "northeast",
  },
] as const;

export function createInitialFeatureValues(features: readonly FeatureSchema[]): FeatureFormValues {
  const values: Partial<FeatureFormValues> = {};

  features.forEach((feature) => {
    if (feature.type === "number") {
      values[feature.id] = String(feature.defaultValue);
      return;
    }

    values[feature.id] = feature.defaultValue;
  });

  return values as FeatureFormValues;
}
