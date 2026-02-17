from pathlib import Path

__version__ = "0.1.0"

# Absolute project paths used across scripts and services.
PACKAGE_DIR = Path(__file__).resolve().parent
SRC_DIR = PACKAGE_DIR.parent
BACKEND_DIR = SRC_DIR.parent
PROJECT_DIR = BACKEND_DIR.parent
DATA_DIR = BACKEND_DIR / "data"
MODELS_DIR = BACKEND_DIR / "models"
NOTEBOOKS_DIR = BACKEND_DIR / "notebooks"
FRONTEND_STATIC_DIR = PACKAGE_DIR / "frontend"
