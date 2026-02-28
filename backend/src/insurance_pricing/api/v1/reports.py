from __future__ import annotations

import re
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

router = APIRouter(prefix="/reports", tags=["reports"])

REPORTS_DIR = Path(__file__).resolve().parents[4] / "reports"
EDA_REPORT_PATH = REPORTS_DIR / "eda_report.md"
EVALUATION_REPORT_PATH = REPORTS_DIR / "evaluation_report.md"
EDA_ASSETS_BASE_URL = "/reports/eda/assets"
MARKDOWN_IMAGE_PATTERN = re.compile(
    r"!\[(?P<alt>[^\]]*)\]\((?P<url>[^)\s]+)(?P<title>\s+\"[^\"]*\")?\)",
)


def _is_relative_url(url: str) -> bool:
    lowered = url.lower()
    return not (
        lowered.startswith("http://")
        or lowered.startswith("https://")
        or lowered.startswith("/")
        or lowered.startswith("#")
        or lowered.startswith("data:")
    )


def _rewrite_eda_markdown_images(markdown: str) -> str:
    def replace(match: re.Match[str]) -> str:
        alt = match.group("alt")
        raw_url = match.group("url")
        title = match.group("title") or ""

        if not _is_relative_url(raw_url):
            return match.group(0)

        normalized_url = raw_url.removeprefix("./")
        return f"![{alt}]({EDA_ASSETS_BASE_URL}/{normalized_url}{title})"

    return MARKDOWN_IMAGE_PATTERN.sub(replace, markdown)


def _read_markdown_or_404(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as error:
        raise HTTPException(status_code=404, detail="Report not found") from error


@router.get("/eda/assets/{path:path}")
async def get_eda_asset(path: str) -> FileResponse:
    requested_path = (REPORTS_DIR / path).resolve(strict=False)

    if not requested_path.is_relative_to(REPORTS_DIR):
        raise HTTPException(status_code=404, detail="Asset not found")

    if not requested_path.exists() or not requested_path.is_file():
        raise HTTPException(status_code=404, detail="Asset not found")

    return FileResponse(path=requested_path)
