# Frontend Static Output

Place the compiled frontend bundle in this directory.

Expected minimum layout:

```text
backend/src/insurance_pricing/frontend/
├── index.html
└── ...asset files/folders...
```

At runtime:
- `GET /` returns `backend/src/insurance_pricing/frontend/index.html` (if present).
- Static assets are served from `GET /static/...`.

If `index.html` is missing, the backend falls back to a minimal placeholder HTML.
