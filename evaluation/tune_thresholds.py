import sys
from src.config import settings

assert "tune" in settings.tune_slice_path.lower(), "tune_thresholds.py must ONLY read the tune slice to prevent data contamination."

print("Tune slice valid. Running threshold tuning...")
# Tuning logic...
