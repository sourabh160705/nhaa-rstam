"""SVI (Stress Vulnerability Index) computation engine.

Produces a composite score 0-100 from multiple analysis components with
weight redistribution for missing components.
"""
import datetime
from ..models.enums import RiskLevel


class SVIEngine:
    def __init__(self):
        self.weights = {
            "acoustic_distress": 0.20,
            "voice_emotion": 0.15,
            "text_sentiment": 0.15,
            "trauma_keywords": 0.20,
            "suicidal_ideation": 0.15,
            "contextual": 0.15
        }
        self.emotion_weights = {
            "fearful": 1.0, "fear": 1.0,
            "sad": 0.8, "sadness": 0.8,
            "angry": 0.6, "anger": 0.6,
            "disgusted": 0.5, "disgust": 0.5,
            "surprised": 0.3, "surprise": 0.3,
            "neutral": 0.1,
            "happy": 0.0, "joy": 0.0,
        }

    def compute(self, voice_result: dict | None, text_result: dict | None, context_data: dict | None = None) -> dict:
        scores = {}

        # ── Acoustic Distress (0-100) ──
        if voice_result and "acoustic_distress" in voice_result:
            scores["acoustic_distress"] = min(100.0, max(0.0, float(voice_result["acoustic_distress"])))

        # ── Voice Emotion (0-100) ──
        if voice_result and "voice_emotion" in voice_result:
            emotion_dist = voice_result["voice_emotion"]
            if emotion_dist:
                emotion_score = sum(
                    prob * self.emotion_weights.get(emo.lower(), 0.3)
                    for emo, prob in emotion_dist.items()
                ) * 100
                scores["voice_emotion"] = min(100.0, max(0.0, emotion_score))

        # ── Text Sentiment (0-100) ──
        # Sentiment ranges from -1 (very negative) to +1 (very positive)
        # Map: -1 → 100 (max distress), 0 → 50 (neutral), +1 → 0 (no distress)
        if text_result and "sentiment" in text_result:
            sentiment = float(text_result["sentiment"])
            # Clamp to [-1, 1]
            sentiment = max(-1.0, min(1.0, sentiment))
            # Non-linear mapping: make moderate negativity produce moderate scores
            if sentiment < 0:
                # Negative: map -1→100, 0→50 with slight curve
                text_sent_score = 50 + (-sentiment) * 50
            else:
                # Positive: map 0→50, 1→0
                text_sent_score = 50 - sentiment * 50
            scores["text_sentiment"] = round(text_sent_score, 2)

        # ── Trauma Keywords (0-100) ──
        if text_result and "trauma_score" in text_result:
            raw_trauma = float(text_result["trauma_score"])
            scores["trauma_keywords"] = min(100.0, max(0.0, raw_trauma))

        # ── Suicidal Ideation (0 or 50-100) ──
        suicidal_flag = False
        if text_result and "suicidal_ideation" in text_result:
            si = text_result["suicidal_ideation"]
            if si.get("flag"):
                suicidal_flag = True
                confidence = float(si.get("confidence", 1.0))
                # Scale: confidence 0.3 → 50, confidence 1.0 → 100
                scores["suicidal_ideation"] = 50 + confidence * 50
            else:
                scores["suicidal_ideation"] = 0.0

        # ── Contextual Vulnerability (0-100) ──
        if context_data:
            context_score = 0
            factors = ["prior_complaints", "displacement", "social_isolation", "prior_violence", "prolonged_legal"]
            for factor in factors:
                if context_data.get(factor):
                    context_score += 20
            scores["contextual"] = min(100.0, float(context_score))

        # ── Weight redistribution for missing components ──
        available_weights = {k: v for k, v in self.weights.items() if k in scores}
        missing_weight_total = sum(v for k, v in self.weights.items() if k not in scores)

        if available_weights:
            redistribution = missing_weight_total / len(available_weights)
            adjusted_weights = {k: v + redistribution for k, v in available_weights.items()}
            total_score = sum(scores[k] * adjusted_weights[k] for k in scores)
        else:
            total_score = 0.0

        # Clamp final score
        total_score = round(min(100.0, max(0.0, total_score)), 2)

        # ── Auto-escalation for suicidal ideation ──
        auto_escalated = False
        escalation_reason = None

        if suicidal_flag:
            total_score = max(total_score, 76.0)
            auto_escalated = True
            escalation_reason = "Suicidal ideation detected"

        risk_level = self._get_risk_level(total_score)

        # Build component details with weights
        components = []
        for k, raw in scores.items():
            w = available_weights.get(k, 0) + (redistribution if available_weights else 0) if available_weights else 0
            components.append({
                "name": k,
                "raw_score": round(raw, 2),
                "weight": round(w, 4) if available_weights else 0,
                "weighted_score": round(raw * w, 2) if available_weights else 0,
            })

        return {
            "total_score": total_score,
            "components": components,
            "risk_level": risk_level,
            "auto_escalated": auto_escalated,
            "escalation_reason": escalation_reason,
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
        }

    def _get_risk_level(self, score: float) -> RiskLevel:
        if score <= 25:
            return RiskLevel.LOW
        elif score <= 50:
            return RiskLevel.MODERATE
        elif score <= 75:
            return RiskLevel.HIGH
        else:
            return RiskLevel.CRITICAL
