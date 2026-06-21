# ai/ollama_client.py — P3-B: Client Ollama (IA locale, fallback gratuit)

from __future__ import annotations
import json
import logging
import requests
from typing import List, Dict

logger = logging.getLogger("OllamaClient")


class OllamaClient:
    """
    Client pour Ollama (IA locale — aucun coût, aucune dépendance réseau externe).

    Modèles recommandés pour l'analyse financière :
      - llama3          (8B, rapide, bon généraliste)
      - llama3:70b      (70B, meilleure qualité, plus lent)
      - mistral         (7B, très rapide)
      - mixtral         (MoE, bonne qualité)
      - deepseek-r1:8b  (raisonnement structuré)

    Installation Ollama : https://ollama.ai
    Lancer un modèle  : ollama run llama3
    """

    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        model:    str = "llama3",
        timeout:  int = 120,
    ):
        self.base_url = base_url.rstrip("/")
        self.model    = model
        self.timeout  = timeout

    def is_available(self) -> bool:
        """Vérifie si Ollama est démarré et accessible."""
        try:
            r = requests.get(f"{self.base_url}/api/tags", timeout=3)
            return r.status_code == 200
        except Exception:
            return False

    def list_models(self) -> List[str]:
        """Liste les modèles disponibles localement."""
        try:
            r = requests.get(f"{self.base_url}/api/tags", timeout=5)
            data = r.json()
            return [m["name"] for m in data.get("models", [])]
        except Exception:
            return []

    def chat(
        self,
        messages:    List[Dict[str, str]],
        system:      str   = None,
        temperature: float = 0.7,
        max_tokens:  int   = 2048,
    ) -> str:
        """
        Envoie une requête chat à Ollama.

        Args:
            messages:    [{"role": "user"|"assistant", "content": str}]
            system:      Prompt système optionnel
            temperature: Créativité (0 = déterministe)
            max_tokens:  Longueur max de la réponse

        Returns:
            str — réponse du modèle
        """
        if not self.is_available():
            return (
                "⚠ Ollama n'est pas démarré. "
                "Lancez-le avec : ollama serve && ollama run llama3"
            )

        payload_messages = []
        if system:
            payload_messages.append({"role": "system", "content": system})
        payload_messages.extend(messages)

        payload = {
            "model":    self.model,
            "messages": payload_messages,
            "stream":   False,
            "options": {
                "temperature":  temperature,
                "num_predict":  max_tokens,
            },
        }

        try:
            r = requests.post(
                f"{self.base_url}/api/chat",
                json=payload,
                timeout=self.timeout,
            )
            r.raise_for_status()
            data = r.json()
            return data["message"]["content"]
        except requests.exceptions.Timeout:
            logger.error("Ollama timeout — modèle trop lent ou surcharge")
            return "⚠ Timeout Ollama. Essayez un modèle plus léger (ex: mistral)."
        except requests.exceptions.HTTPError as e:
            logger.error(f"Ollama HTTP error: {e}")
            return f"⚠ Erreur Ollama {e.response.status_code}"
        except Exception as e:
            logger.error(f"Ollama request failed: {e}")
            return f"⚠ Erreur Ollama : {e}"