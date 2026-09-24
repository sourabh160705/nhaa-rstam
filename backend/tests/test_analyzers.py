"""Unit tests for text analysis modules."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
from app.analyzers.trauma_keywords import TraumaKeywordAnalyzer
from app.analyzers.sentiment import TextSentimentAnalyzer
from app.analyzers.suicidal_ideation import SuicidalIdeationDetector
from app.analyzers.language_detect import LanguageDetector
from app.utils.anonymizer import PIIAnonymizer


class TestTraumaKeywords:
    def setup_method(self):
        self.analyzer = TraumaKeywordAnalyzer()

    def test_violence_keywords(self):
        text = "My husband was beaten and murdered by them. They attacked us with rods."
        result = self.analyzer.analyze(text)
        assert len(result["matches"]) > 0
        assert any(m["category"] == "VIOLENCE" for m in result["matches"])
        assert result["keyword_density_score"] > 0

    def test_discrimination_keywords(self):
        text = "They practice untouchability in our village. We are boycotted from using the well."
        result = self.analyzer.analyze(text)
        assert any(m["category"] == "DISCRIMINATION" for m in result["matches"])

    def test_no_trauma(self):
        text = "I want to know about the legal provisions available for protection."
        result = self.analyzer.analyze(text)
        assert result["keyword_density_score"] < 20

    def test_multiple_categories(self):
        text = "They beat us, boycotted us, and threatened to kill us if we file FIR."
        result = self.analyzer.analyze(text)
        categories = set(m["category"] for m in result["matches"])
        assert len(categories) >= 2


class TestSentiment:
    def setup_method(self):
        self.analyzer = TextSentimentAnalyzer()

    def test_negative_sentiment(self):
        text = "I am terrified and hopeless. Nobody helps us. We are suffering."
        result = self.analyzer.analyze(text)
        assert result["sentiment_score"] < 0

    def test_neutral_sentiment(self):
        text = "I would like information about filing a complaint under the Act."
        result = self.analyzer.analyze(text)
        assert -0.3 <= result["sentiment_score"] <= 0.3

    def test_empty_text(self):
        result = self.analyzer.analyze("")
        assert result["sentiment_score"] == 0.0


class TestSuicidalIdeation:
    def setup_method(self):
        self.detector = SuicidalIdeationDetector()

    def test_explicit_detection(self):
        text = "I want to kill myself. There is no point in living anymore."
        result = self.detector.analyze(text)
        assert result["flag"] is True
        assert result["confidence"] > 0.7
        assert len(result["matched_phrases"]) > 0

    def test_implicit_detection(self):
        text = "I feel like there is no hope left and I am a burden to everyone."
        result = self.detector.analyze(text)
        assert result["flag"] is True

    def test_no_detection(self):
        text = "I want to file a complaint about discrimination at my workplace."
        result = self.detector.analyze(text)
        assert result["flag"] is False

    def test_high_sensitivity(self):
        text = "Nobody cares about us. What is the point of all this?"
        result = self.detector.analyze(text)
        # High sensitivity mode should catch implicit patterns
        assert result["flag"] is True or result["confidence"] > 0


class TestPIIAnonymizer:
    def setup_method(self):
        self.anonymizer = PIIAnonymizer()

    def test_phone_redaction(self):
        text = "Call me at +91 9876543210 or 9876543210."
        result = self.anonymizer.anonymize(text)
        assert "9876543210" not in result["anonymized_text"]
        assert "[PHONE_REDACTED]" in result["anonymized_text"]

    def test_aadhaar_redaction(self):
        text = "My Aadhaar number is 1234-5678-9012."
        result = self.anonymizer.anonymize(text)
        assert "1234-5678-9012" not in result["anonymized_text"]

    def test_email_redaction(self):
        text = "Email me at victim@example.com for details."
        result = self.anonymizer.anonymize(text)
        assert "victim@example.com" not in result["anonymized_text"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
