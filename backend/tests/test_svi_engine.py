"""Unit tests for the SVI computation engine."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
from app.services.svi_engine import SVIEngine
from app.models.enums import RiskLevel


class TestSVIEngine:
    """Test suite for SVIEngine."""

    def setup_method(self):
        self.engine = SVIEngine()

    def test_compute_text_only_low_risk(self):
        """Text-only assessment with neutral sentiment should yield LOW risk."""
        text_result = {
            "sentiment": 0.3,
            "trauma_score": 5.0,
            "suicidal_ideation": {"flag": False, "confidence": 0.0},
        }
        result = self.engine.compute(voice_result=None, text_result=text_result)
        assert result["total_score"] <= 25
        assert result["risk_level"] == RiskLevel.LOW
        assert result["auto_escalated"] is False

    def test_compute_text_moderate_risk(self):
        """Moderate negative sentiment and some trauma keywords."""
        text_result = {
            "sentiment": -0.4,
            "trauma_score": 40.0,
            "suicidal_ideation": {"flag": False, "confidence": 0.0},
        }
        result = self.engine.compute(voice_result=None, text_result=text_result)
        assert 26 <= result["total_score"] <= 50
        assert result["risk_level"] == RiskLevel.MODERATE

    def test_compute_high_risk(self):
        """High trauma score with fearful voice emotion."""
        voice_result = {
            "acoustic_distress": 65.0,
            "voice_emotion": {"fearful": 0.7, "sad": 0.2, "neutral": 0.1},
        }
        text_result = {
            "sentiment": -0.7,
            "trauma_score": 70.0,
            "suicidal_ideation": {"flag": False, "confidence": 0.0},
        }
        result = self.engine.compute(voice_result=voice_result, text_result=text_result)
        assert result["total_score"] > 50
        assert result["risk_level"] in (RiskLevel.HIGH, RiskLevel.CRITICAL)

    def test_suicidal_ideation_auto_escalation(self):
        """Suicidal ideation should auto-escalate to CRITICAL."""
        text_result = {
            "sentiment": -0.3,
            "trauma_score": 20.0,
            "suicidal_ideation": {"flag": True, "confidence": 0.85},
        }
        result = self.engine.compute(voice_result=None, text_result=text_result)
        assert result["total_score"] >= 76
        assert result["risk_level"] == RiskLevel.CRITICAL
        assert result["auto_escalated"] is True
        assert "suicidal" in result["escalation_reason"].lower()

    def test_empty_input(self):
        """No input should return score 0 with LOW risk."""
        result = self.engine.compute(voice_result=None, text_result=None)
        assert result["total_score"] == 0
        assert result["risk_level"] == RiskLevel.LOW

    def test_contextual_vulnerability(self):
        """Context data should increase the SVI score."""
        text_result = {
            "sentiment": -0.2,
            "trauma_score": 30.0,
            "suicidal_ideation": {"flag": False, "confidence": 0.0},
        }
        context = {
            "prior_complaints": True,
            "displacement": True,
            "social_isolation": True,
            "prior_violence": False,
            "prolonged_legal": True,
        }
        result_no_ctx = self.engine.compute(voice_result=None, text_result=text_result)
        result_ctx = self.engine.compute(voice_result=None, text_result=text_result, context_data=context)
        assert result_ctx["total_score"] > result_no_ctx["total_score"]

    def test_weight_redistribution(self):
        """When voice data is missing, weights should be redistributed."""
        text_result = {
            "sentiment": -0.5,
            "trauma_score": 50.0,
            "suicidal_ideation": {"flag": False, "confidence": 0.0},
        }
        result = self.engine.compute(voice_result=None, text_result=text_result)
        # Should still produce a valid score even without voice data
        assert 0 <= result["total_score"] <= 100
        assert result["risk_level"] is not None

    def test_components_present(self):
        """Result should include component breakdown."""
        text_result = {
            "sentiment": -0.5,
            "trauma_score": 50.0,
            "suicidal_ideation": {"flag": False, "confidence": 0.0},
        }
        result = self.engine.compute(voice_result=None, text_result=text_result)
        assert "components" in result
        assert len(result["components"]) > 0
        assert all("name" in c and "raw_score" in c for c in result["components"])

    def test_risk_level_boundaries(self):
        """Test exact boundary values for risk levels."""
        assert self.engine._get_risk_level(0) == RiskLevel.LOW
        assert self.engine._get_risk_level(25) == RiskLevel.LOW
        assert self.engine._get_risk_level(26) == RiskLevel.MODERATE
        assert self.engine._get_risk_level(50) == RiskLevel.MODERATE
        assert self.engine._get_risk_level(51) == RiskLevel.HIGH
        assert self.engine._get_risk_level(75) == RiskLevel.HIGH
        assert self.engine._get_risk_level(76) == RiskLevel.CRITICAL
        assert self.engine._get_risk_level(100) == RiskLevel.CRITICAL


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
