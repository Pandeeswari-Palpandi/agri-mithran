import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
INDEX_PATH = PROJECT_ROOT / "faiss_tn_agri_index"
PDF_PATH = PROJECT_ROOT / "data" / "tamilnadu.pdf"
SOURCES = (
    "https://agritech.tnau.ac.in/expert_system/paddy/Schemes.html#cs",
    "https://aed.tn.gov.in/en/individual-based-subsidy-schemes/",
    "https://arivark.com/tamil-nadu-government-schemes/"
    "tamil-nadu-agriculture-budget-2026-27-highlights#en",
    "https://agritech.tnau.ac.in/agricultural_engineering/"
    "agriengg_govt_schemes.html",
)

load_dotenv(PROJECT_ROOT / ".env")
os.environ.setdefault("USER_AGENT", "AgriMithranBot/1.0")
