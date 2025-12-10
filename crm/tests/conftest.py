import sys
from pathlib import Path

# Ensure the repository root is on the Python path so "crm" can be imported in tests.
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
