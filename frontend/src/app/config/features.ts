import type { PredictRequest, Region, Sex, Smoker } from "@/app/types/api";

type FeatureKey = keyof PredictRequest;

interface BaseFeatureDefinition<K extends FeatureKey, T extends "numeric" | "categorical"> {
  key: K;
  type: T;
  label: string;
  description?: string;
  order?: number;
  group?: string;
}

export interface NumericFeatureDefinition<K extends FeatureKey = FeatureKey>
  extends BaseFeatureDefinition<K, "numeric"> {
  min: number;
  max: number;
  step: number;
  defaultValue: number;
}

export interface CategoricalFeatureDefinition<
  K extends FeatureKey = FeatureKey,
  O extends string = string,
> extends BaseFeatureDefinition<K, "categorical"> {
  options: readonly O[];
  defaultValue: O;
}

export type FeatureDefinition = NumericFeatureDefinition | CategoricalFeatureDefinition;

const SEX_OPTIONS = ["female", "male"] as const satisfies readonly Sex[];
const SMOKER_OPTIONS = ["no", "yes"] as const satisfies readonly Smoker[];
const REGION_OPTIONS = ["northeast", "northwest", "southeast", "southwest"] as const satisfies readonly Region[];

export const FEATURE_DEFINITIONS: readonly FeatureDefinition[] = [
  {
    key: "age",
    type: "numeric",
    label: "Age",
    description: "Age in years",
    min: 18,
    max: 100,
    step: 1,
    defaultValue: 35,
    order: 1,
    group: "Profile",
  },
  {
    key: "sex",
    type: "categorical",
    label: "Sex",
    options: SEX_OPTIONS,
    defaultValue: "female",
    order: 2,
    group: "Profile",
  },
  {
    key: "bmi",
    type: "numeric",
    label: "BMI",
    description: "Body mass index",
    min: 10,
    max: 60,
    step: 0.1,
    defaultValue: 27.5,
    order: 3,
    group: "Health",
  },
  {
    key: "children",
    type: "numeric",
    label: "Children",
    description: "Number of dependents",
    min: 0,
    max: 6,
    step: 1,
    defaultValue: 0,
    order: 4,
    group: "Household",
  },
  {
    key: "smoker",
    type: "categorical",
    label: "Smoker",
    options: SMOKER_OPTIONS,
    defaultValue: "no",
    order: 5,
    group: "Health",
  },
  {
    key: "region",
    type: "categorical",
    label: "Region",
    options: REGION_OPTIONS,
    defaultValue: "northeast",
    order: 6,
    group: "Location",
  },
] as const;

export function createDefaultInputs(
  definitions: readonly FeatureDefinition[],
): PredictRequest {
  const defaults: Partial<PredictRequest> = {};

  definitions.forEach((feature) => {
    defaults[feature.key] = feature.defaultValue as PredictRequest[typeof feature.key];
  });

  return defaults as PredictRequest;
}
