from pydantic import BaseModel


class EdaReportResponse(BaseModel):
    title: str
    markdown: str
    assets_base_url: str


class EvaluationReportResponse(BaseModel):
    title: str
    markdown: str
