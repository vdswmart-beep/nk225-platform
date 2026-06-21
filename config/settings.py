# config/settings.py — UPDATED: support Groq (gsk_) + Grok (xai-) + Ollama

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

try:
    from dotenv import load_dotenv
    load_dotenv(ROOT / ".env")
except ImportError:
    pass

# ── Data ──────────────────────────────────────────────────────────────
DATA_MODE       = os.getenv("DATA_MODE", "backtest")
BACKTEST_START  = "2022-01-01"
BACKTEST_END    = "2026-01-01"
CACHE_TTL_HOURS = 24

# ── Dashboard ─────────────────────────────────────────────────────────
DASH_HOST  = os.getenv("DASH_HOST", "127.0.0.1")
DASH_PORT  = int(os.getenv("DASH_PORT", "8050"))
DASH_DEBUG = os.getenv("DASH_DEBUG", "false").lower() == "true"

# ── AI Provider ───────────────────────────────────────────────────────
# AI_PROVIDER auto-détecté depuis les clés disponibles si non spécifié :
#   gsk_...  → groq   (Llama/Mistral via Groq, gratuit)
#   xai-...  → grok   (Grok-3 via xAI, payant)
#   ollama   → ollama (local)

_GROK_KEY  = os.getenv("GROK_API_KEY", "")
_GROQ_KEY  = os.getenv("GROQ_API_KEY", "")

def _auto_detect_provider():
    explicit = os.getenv("AI_PROVIDER", "").lower()
    if explicit in ("groq", "grok", "ollama"):
        return explicit
    if _GROQ_KEY.startswith("gsk_"):
        return "groq"
    if _GROK_KEY.startswith("xai-"):
        return "grok"
    if os.getenv("USE_OLLAMA", "false").lower() == "true":
        return "ollama"
    return "none"

AI_PROVIDER = _auto_detect_provider()

# Grok (xAI)
GROK_API_KEY  = _GROK_KEY
GROK_BASE_URL = "https://api.x.ai/v1"
GROK_MODEL    = os.getenv("GROK_MODEL", "grok-3")

# Groq
GROQ_API_KEY  = _GROQ_KEY
GROQ_BASE_URL = "https://api.groq.com/openai/v1"
GROQ_MODEL    = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

# Ollama (local)
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL    = os.getenv("OLLAMA_MODEL", "llama3")
USE_OLLAMA      = AI_PROVIDER == "ollama"

# ── Portfolio ─────────────────────────────────────────────────────────
DEFAULT_METHOD      = os.getenv("PORTFOLIO_METHOD", "risk_parity")
MAX_POSITION_WEIGHT = float(os.getenv("MAX_POSITION_WEIGHT", "0.15"))
MIN_POSITION_WEIGHT = float(os.getenv("MIN_POSITION_WEIGHT", "-0.10"))
TARGET_GROSS        = 1.0

# ── Risk ──────────────────────────────────────────────────────────────
VAR_CONFIDENCE  = 0.95
CVAR_CONFIDENCE = 0.95

# ── Paths ─────────────────────────────────────────────────────────────
CACHE_DIR   = ROOT / "cache" / "yahoo"
OUTPUTS_DIR = ROOT / "outputs"
LOGS_DIR    = ROOT / "logs"

for p in [CACHE_DIR, OUTPUTS_DIR, LOGS_DIR]:
    p.mkdir(parents=True, exist_ok=True)