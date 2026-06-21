# ai/groq_client.py — Client Groq (clé gsk_..., modèles Llama/Mistral rapides)
#
# IMPORTANT : Groq ≠ Grok
#   Groq   → https://console.groq.com  | clé gsk_...  | Llama, Mistral, Gemma
#   Grok   → https://console.x.ai      | clé xai-...  | Grok-3 (xAI)
#
# Groq est OpenAI-compatible, très rapide (LPU), et gratuit sur le free tier.
# Modèles recommandés pour l'analyse financière :
#   - llama-3.3-70b-versatile   (meilleure qualité)
#   - llama-3.1-8b-instant      (ultra rapide)
#   - mixtral-8x7b-32768        (bon contexte long)

import logging
import requests
from typing import List, Dict

logger = logging.getLogger("GroqClient")

GROQ_BASE_URL = "https://api.groq.com/openai/v1"
GROQ_DEFAULT_MODEL = "llama-3.3-70b-versatile"


class GroqClient:
    """Client pour l'API Groq (OpenAI-compatible)."""

    def __init__(self, api_key: str = None, model: str = None):
        self.api_key  = api_key  or ""
        self.model    = model    or GROQ_DEFAULT_MODEL
        self.base_url = GROQ_BASE_URL
        self._headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type":  "application/json",
        }

    def is_available(self) -> bool:
        return bool(self.api_key) and self.api_key.startswith("gsk_")

    def chat(
        self,
        messages:    List[Dict[str, str]],
        system:      str   = None,
        temperature: float = 0.7,
        max_tokens:  int   = 2048,
    ) -> str:
        if not self.is_available():
            return (
                "⚠ Clé Groq non configurée.\n"
                "Ajoutez dans .env :\n"
                "  GROQ_API_KEY=gsk_votre_clé\n"
                "  AI_PROVIDER=groq\n"
                "Obtenez une clé gratuite sur https://console.groq.com"
            )

        payload_messages = []
        if system:
            payload_messages.append({"role": "system", "content": system})
        payload_messages.extend(messages)

        payload = {
            "model":       self.model,
            "messages":    payload_messages,
            "temperature": temperature,
            "max_tokens":  max_tokens,
        }

        try:
            resp = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self._headers,
                json=payload,
                timeout=60,
            )
            resp.raise_for_status()
            return resp.json()["choices"][0]["message"]["content"]
        except requests.exceptions.HTTPError as e:
            logger.error(f"Groq HTTP error: {e.response.status_code} — {e.response.text[:200]}")
            return f"Erreur API Groq {e.response.status_code}: {e.response.text[:200]}"
        except Exception as e:
            logger.error(f"Groq request failed: {e}")
            return f"Erreur Groq : {e}"