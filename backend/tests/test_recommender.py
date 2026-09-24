"""Unit tests for the intervention recommender."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
from app.services.recommender import InterventionRecommender


class TestRecommender:
    def setup_method(self):
        self.recommender = InterventionRecommender()

    def test_low_risk_recommendations(self):
        svi = {"total_score": 15, "components": []}
        recs = self.recommender.recommend("LOW", svi)
        assert len(recs) >= 2
        # Should include information and follow-up
        types = [r["intervention_type"] for r in recs]
        assert any("INFORMATION" in t for t in types)

    def test_critical_risk_recommendations(self):
        svi = {"total_score": 90, "components": []}
        recs = self.recommender.recommend("CRITICAL", svi)
        assert len(recs) >= 4
        types = [r["intervention_type"] for r in recs]
        assert any("POLICE" in t or "EMERGENCY" in t for t in types)

    def test_suicidal_ideation_prepends_crisis(self):
        svi = {"total_score": 85, "components": []}
        text_analysis = {"suicidal_ideation": {"flag": True, "confidence": 0.9}}
        recs = self.recommender.recommend("CRITICAL", svi, text_analysis)
        # First recommendation should be crisis counselling
        assert recs[0]["priority"] == 0 or "crisis" in recs[0]["description"].lower() or "suicid" in recs[0]["description"].lower()

    def test_recommendations_have_required_fields(self):
        svi = {"total_score": 40, "components": []}
        recs = self.recommender.recommend("MODERATE", svi)
        for rec in recs:
            assert "intervention_type" in rec
            assert "priority" in rec
            assert "description" in rec
            assert "response_sla" in rec


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
