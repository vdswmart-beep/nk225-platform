# ai/ai_router.py — UPDATED: auto-détecte Groq (gsk_) / Grok (xai-) / Ollama

from __future__ import annotations
import logging
from typing import List, Dict, Optional

logger = logging.getLogger("AIRouter")


class AIRouter:
    """
    Router IA transparent.

    Priorité auto-détectée depuis config/settings.py :
      1. Groq  si GROQ_API_KEY=gsk_...  (rapide, gratuit)
      2. Grok  si GROK_API_KEY=xai-...  (xAI, payant)
      3. Ollama si USE_OLLAMA=true       (local)
    """

    def __init__(self):
        from config.settings import (
            AI_PROVIDER,
            GROK_API_KEY, GROK_MODEL, GROK_BASE_URL,
            GROQ_API_KEY, GROQ_MODEL,
            OLLAMA_BASE_URL, OLLAMA_MODEL,
        )
        self._provider      = None
        self._provider_name = "none"

        logger.info(f"AI Provider détecté : {AI_PROVIDER}")

        if AI_PROVIDER == "groq":
            self._init_groq(GROQ_API_KEY, GROQ_MODEL)
        elif AI_PROVIDER == "grok":
            self._init_grok(GROK_API_KEY, GROK_MODEL)
        elif AI_PROVIDER == "ollama":
            self._init_ollama(OLLAMA_BASE_URL, OLLAMA_MODEL)
        else:
            logger.warning(
                "Aucun provider IA configuré.\n"
                "  → Groq (gratuit) : ajoutez GROQ_API_KEY=gsk_... dans .env\n"
                "  → Grok (xAI)     : ajoutez GROK_API_KEY=xai-... dans .env\n"
                "  → Ollama (local) : USE_OLLAMA=true dans .env"
            )

    def _init_groq(self, key, model):
        try:
            from ai.groq_client import GroqClient
            client = GroqClient(api_key=key, model=model)
            if client.is_available():
                self._provider      = client
                self._provider_name = f"Groq ({model})"
                logger.info(f"✓ {self._provider_name}")
            else:
                logger.warning("Clé Groq invalide ou absente")
        except Exception as e:
            logger.error(f"Groq init: {e}")

    def _init_grok(self, key, model):
        try:
            from ai.grok_client import GrokClient
            client = GrokClient(api_key=key, model=model)
            self._provider      = client
            self._provider_name = f"Grok ({model})"
            logger.info(f"✓ {self._provider_name}")
        except Exception as e:
            logger.error(f"Grok init: {e}")

    def _init_ollama(self, url, model):
        try:
            from ai.ollama_client import OllamaClient
            client = OllamaClient(base_url=url, model=model)
            if client.is_available():
                self._provider      = client
                self._provider_name = f"Ollama ({model})"
                logger.info(f"✓ {self._provider_name}")
            else:
                logger.warning("Ollama non disponible (lancez : ollama serve)")
        except Exception as e:
            logger.error(f"Ollama init: {e}")

    @property
    def provider_name(self):
        return self._provider_name

    @property
    def is_available(self):
        return self._provider is not None

    def chat(self, messages, system=None, temperature=0.7, max_tokens=2048):
        if self._provider is None:
            return (
                "⚠ Aucun provider IA configuré.\n\n"
                "Option 1 — Groq (gratuit, rapide) :\n"
                "  Clé sur https://console.groq.com\n"
                "  Ajoutez dans .env : GROQ_API_KEY=gsk_...\n\n"
                "Option 2 — Grok xAI :\n"
                "  Clé sur https://console.x.ai\n"
                "  Ajoutez dans .env : GROK_API_KEY=xai-...\n\n"
                "Option 3 — Ollama (local) :\n"
                "  brew install ollama && ollama run llama3\n"
                "  Ajoutez dans .env : USE_OLLAMA=true"
            )
        return self._provider.chat(
            messages=messages, system=system,
            temperature=temperature, max_tokens=max_tokens,
        )


_router: Optional[AIRouter] = None


def get_ai_router() -> AIRouter:
    global _router
    if _router is None:
        _router = AIRouter()
    return _router