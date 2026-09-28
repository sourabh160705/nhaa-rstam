import pytest
import asyncio
from unittest.mock import patch, AsyncMock
from app.services.llm_analyzer import LLMAnalyzer
from app.services.text_pipeline import TextPipeline

@pytest.fixture
def anyio_backend():
    return 'asyncio'

@pytest.mark.anyio
async def test_llm_analyzer_not_configured():
    analyzer = LLMAnalyzer()
    analyzer.api_key = ""
    assert not analyzer.is_configured()
    res = await analyzer.analyze("test text")
    assert res is None

@pytest.mark.anyio
async def test_text_pipeline_fallback_when_llm_unconfigured():
    pipeline = TextPipeline()
    pipeline.llm.api_key = ""  # ensure unconfigured
    res = await pipeline.process("i am not feeling well", language="en")
    assert res["trauma_score"] == 0.0
    assert not res["llm_enhanced"]

@pytest.mark.anyio
async def test_text_pipeline_uses_llm_when_available():
    pipeline = TextPipeline()
    pipeline.llm.api_key = "gsk_dummy_mock_key"
    
    mock_llm_output = {
        "detected_language": "en",
        "translated_text": "The local bullies entered our house and threatened us.",
        "trauma_score": 68.0,
        "trauma_categories": ["VIOLENCE", "THREATS"],
        "trauma_keywords": [{"keyword": "bullies", "category": "VIOLENCE", "severity": 4}],
        "sentiment": -0.7,
        "sentiment_label": "very_negative",
        "dominant_emotion": "fear",
        "suicidal_ideation": {"flag": False, "confidence": 0.0, "risk_level": "none", "matched_phrases": []},
        "legal_violations": ["Section 3(1)(r) SC/ST PoA Act"],
        "recommendations": [
            {
                "intervention_type": "LEGAL_AID",
                "priority": 2,
                "description": "Register FIR under Section 3(1)(r) PoA Act",
                "action_details": "Assist victim at local police station",
                "response_sla": "4 hours"
            }
        ]
    }

    with patch.object(pipeline.llm, "analyze", new_callable=AsyncMock) as mock_analyze:
        mock_analyze.return_value = mock_llm_output
        res = await pipeline.process("The local bullies entered our house and threatened us.")
        
        assert res["llm_enhanced"] is True
        assert res["trauma_score"] == 68.0
        assert "VIOLENCE" in res["trauma_categories"]
        assert len(res["legal_violations"]) == 1
        assert len(res["customized_recommendations"]) == 1
