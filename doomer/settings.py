from pathlib import Path
from os import getenv

from dotenv import load_dotenv


ROOT_DIR = Path(__file__).parent.parent
MODELS_DIR = ROOT_DIR / "models"
DATA_DIR = ROOT_DIR / "data"
SETTINGS_DIR = ROOT_DIR / "settings"
DOCS_DIR = ROOT_DIR / "docs"

HELP_FILE = DOCS_DIR / "usage.md"
DOTENV_PATH = ROOT_DIR / ".env"

COGS_PATH = "doomer/cogs"

DEFAULT_MODEL_NAME = "openai-gpt3"

load_dotenv(DOTENV_PATH)

OPENAI_API_KEY = getenv("OPENAI_API_KEY")
EXAFUNCTION_API_KEY = getenv("EXAFUNCTION_API_KEY")
AI21_API_KEY = getenv("AI21_API_KEY")
DISCORD_API_KEY = getenv("DISCORD_API_KEY")
COMMAND_PREFIX = getenv("COMMAND_PREFIX", ">")
