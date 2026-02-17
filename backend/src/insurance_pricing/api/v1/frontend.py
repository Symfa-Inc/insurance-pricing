from fastapi import APIRouter, HTTPException, status
from fastapi.responses import FileResponse, HTMLResponse

from insurance_pricing import FRONTEND_STATIC_DIR

router = APIRouter(tags=["frontend"])


@router.get("/", response_class=HTMLResponse)
async def spa_entrypoint() -> FileResponse:
    index_path = FRONTEND_STATIC_DIR / "index.html"
    if not index_path.exists():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Frontend entrypoint is missing at {index_path}",
        )
    return FileResponse(index_path)
