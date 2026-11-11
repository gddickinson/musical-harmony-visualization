"""Put the repository root on sys.path so the flat modules (theory, synthesis, visualization) import in tests."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
