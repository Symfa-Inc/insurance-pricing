from fastapi import APIRouter
from fastapi.responses import HTMLResponse

SPA_ENTRY_HTML = """<!DOCTYPE html>
<html>
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Insurance Pricing App</title>
  </head>
  <body>
    <div id="app"></div>
    <script>
      console.log("SPA loaded");
    </script>
  </body>
</html>
"""

router = APIRouter(tags=["frontend"])


@router.get("/", response_class=HTMLResponse)
async def spa_entrypoint() -> HTMLResponse:
    return HTMLResponse(content=SPA_ENTRY_HTML)
