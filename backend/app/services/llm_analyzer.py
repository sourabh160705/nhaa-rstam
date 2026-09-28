"""LLM-Powered Semantic Trauma and Legal Analyzer.

Integrates lightweight, ultra-fast LLMs (e.g., Llama 3.1 via Groq) to provide deep,
context-aware trauma assessment, legal SC/ST (PoA) Act analysis, and tailored
police/medical/psychosocial recommendations.
"""
import json
import logging
from typing import Optional, Dict, Any
import httpx

from ..config import settings

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are an expert trauma psychologist and legal advisor for India's National Helpline Against Atrocities (NHAA 14566), serving Scheduled Castes (SC) and Scheduled Tribes (ST) facing discrimination, atrocities, violence, or legal denial under the Scheduled Castes and Scheduled Tribes (Prevention of Atrocities) Act, 1989.

Analyze the victim/complainant statement carefully and return ONLY a valid JSON object matching the following structure:
{
  "detected_language": "en | hi | mr | ta | te | bn | other",
  "translated_text": "English translation if non-English, else original",
  "trauma_score": <number between 0 and 100 representing intensity of trauma/distress>,
  "trauma_categories": [<list of matched categories from: "VIOLENCE", "DISCRIMINATION", "THREATS", "PSYCHOLOGICAL", "SUICIDAL", "LEGAL", "DISPLACEMENT">],
  "trauma_keywords": [
    {"keyword": "<phrase/word>", "category": "<one of above categories>", "severity": <1 to 5>}
  ],
  "sentiment": <float from -1.0 (extreme negative distress) to +1.0 (positive/safe)>,
  "sentiment_label": "very_negative | negative | neutral | positive",
  "dominant_emotion": "fear | sadness | anger | helplessness | joy | neutral",
  "suicidal_ideation": {
    "flag": <true if the victim expresses suicidal thoughts or desire to end their life, else false>,
    "confidence": <float from 0.0 to 1.0>,
    "risk_level": "none | low | moderate | high | severe",
    "matched_phrases": [<quoted phrases from text indicating suicidal ideation>]
  },
  "legal_violations": [
    "<specific violations under SC/ST (PoA) Act, IPC/BNS, e.g., Section 3(1)(r) - Public humiliation, Section 3(1)(g) - Land dispossession, Section 15A - Witness protection>"
  ],
  "recommendations": [
    {
      "intervention_type": "POLICE_DISPATCH | LEGAL_AID | CRISIS_COUNSELING | MEDICAL_ASSISTANCE | WITNESS_PROTECTION | ADMINISTRATIVE_ACTION | SCHEDULED_FOLLOWUP",
      "priority": <1 (Immediate emergency) to 4 (Routine follow-up)>,
      "description": "<Concise action title>",
      "action_details": "<Concrete step for operator/authorities, referencing relevant legal provisions>",
      "response_sla": "<e.g., Immediate (< 15 mins), 2 hours, 24 hours>"
    }
  ]
}

Ensure the analysis is nuanced:
- Mild grievances or inquiries should receive low trauma scores (10-25).
- Moderate distress, discrimination, or procedural delay should receive moderate scores (26-50).
- Physical assault, destruction of property, or social boycotts should receive high scores (51-75).
- Severe violence, rape, murder threats, or suicidal ideation must trigger scores >= 76 with immediate emergency interventions.
"""

class LLMAnalyzer:
    """Handles communication with LLM inference providers."""

    def __init__(self):
        self.api_key = settings.GROQ_API_KEY
        self.base_url = settings.LLM_BASE_URL.rstrip('/')
        self.model = settings.LLM_MODEL

    def is_configured(self) -> bool:
        """Check if LLM inference is enabled and configured."""
        return bool(self.api_key and self.api_key.strip())

    async def analyze(self, text: str, language_hint: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Run deep semantic analysis on narrative text using Llama 3.1.
        
        Returns parsed analysis dictionary or None if LLM is unavailable.
        """
        if not self.is_configured():
            return None

        if not text or not text.strip():
            return None

        user_content = f"Victim/Complainant Narrative:\n\"{text}\""
        if language_hint:
            user_content += f"\n(Language hint: {language_hint})"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_content}
            ],
            "temperature": 0.1,  # Low temperature for deterministic legal assessment
            "response_format": {"type": "json_object"}
        }

        url = f"{self.base_url}/chat/completions"

        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                response = await client.post(url, headers=headers, json=payload)
                if response.status_code != 200:
                    logger.error("LLM API error %d: %s", response.status_code, response.text)
                    return None

                data = response.json()
                content = data["choices"][0]["message"]["content"]
                result = json.loads(content)
                logger.info("Successfully analyzed narrative using %s", self.model)
                return result

        except Exception as e:
            logger.error("Failed to query LLM API: %s", e)
            return None
