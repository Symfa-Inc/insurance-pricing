export interface EdaReportResponse {
  title: string;
  markdown: string;
  assets_base_url: string;
}

export interface EvaluationReportResponse {
  title: string;
  markdown: string;
}

export type ReportResponse = EdaReportResponse | EvaluationReportResponse;
