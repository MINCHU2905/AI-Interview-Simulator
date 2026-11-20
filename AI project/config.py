"""Application configuration and filesystem paths."""
from pathlib import Path
import os

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent
DATABASE_DIR = BASE_DIR / "database"
UPLOAD_DIR = BASE_DIR / "uploads"
PROMPTS_DIR = BASE_DIR / "prompts"
DATABASE_PATH = DATABASE_DIR / "interview.db"

for directory in (DATABASE_DIR, UPLOAD_DIR, PROMPTS_DIR):
    directory.mkdir(parents=True, exist_ok=True)

load_dotenv(BASE_DIR / ".env")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash").strip()
MAX_UPLOAD_SIZE_MB = 10
