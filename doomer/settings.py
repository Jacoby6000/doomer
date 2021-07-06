from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
MODELS_DIR = ROOT_DIR / "models"
DATA_DIR = ROOT_DIR / "data"
SETTINGS_DIR = ROOT_DIR / "settings"
DOCS_DIR = ROOT_DIR / "docs"

HELP_FILE = DOCS_DIR / "usage.md"

DEFAULT_MODEL_NAME = "gpt2"
