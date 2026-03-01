__version__ = "0.1.0"

# Re-export path constants so `train` package imports keep working.
from insurance_pricing.config import DATA_DIR, MODELS_DIR, REPORTS_DIR

__all__ = ["__version__", "DATA_DIR", "MODELS_DIR", "REPORTS_DIR"]
