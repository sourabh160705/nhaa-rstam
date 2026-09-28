"""Text analysis orchestration pipeline.

Coordinates language detection, translation, trauma keyword extraction,
sentiment analysis, and suicidal ideation detection.
Equipped with Next-Gen LLM semantic analysis (Llama 3.1) with automatic
graceful fallback to local rule-based analyzers.
"""
import time
import logging
from typing import Optional

from ..analyzers.language_detect import LanguageDetector
from ..analyzers.translator import TextTranslator
from ..analyzers.trauma_keywords import TraumaKeywordAnalyzer
from ..analyzers.sentiment import TextSentimentAnalyzer
from ..analyzers.suicidal_ideation import SuicidalIdeationDetector
from .llm_analyzer import LLMAnalyzer

logger = logging.getLogger(__name__)


class TextPipeline:
    """Orchestrates text analysis through LLM or local NLP stages."""

    def __init__(self):
        self.llm = LLMAnalyzer()
        self.lang_detector = LanguageDetector()
        self.translator = TextTranslator()
        self.trauma = TraumaKeywordAnalyzer()
        self.sentiment = TextSentimentAnalyzer()
        self.si_detector = SuicidalIdeationDetector()

    async def process(self, text: str, language: Optional[str] = None) -> dict:
        """Process text through the full analysis pipeline.

        Tries deep LLM analysis first (Option B); falls back to local analyzers
        if LLM is unconfigured or unavailable.
        """
        result = {
            "original_text": text,
            "detected_language": language or "en",
            "translated_text": text,
            "trauma_keywords": [],
            "trauma_score": 0.0,
            "trauma_categories": [],
            "sentiment": 0.0,
            "sentiment_label": "neutral",
            "emotion_scores": [],
            "dominant_emotion": "neutral",
            "suicidal_ideation": {"flag": False, "confidence": 0.0, "matched_phrases": [], "risk_level": "none"},
            "legal_violations": [],
            "customized_recommendations": [],
            "llm_enhanced": False,
            "durations": {},
        }

        if not text or not text.strip():
            return result

        # ─── Option B: Next-Gen LLM Semantic Analysis (Llama 3.1) ───
        if self.llm.is_configured():
            llm_start = time.time()
            try:
                llm_res = await self.llm.analyze(text, language_hint=language)
                if llm_res:
                    result["detected_language"] = llm_res.get("detected_language") or language or "en"
                    result["translated_text"] = llm_res.get("translated_text") or text
                    result["trauma_score"] = float(llm_res.get("trauma_score", 0.0))
                    result["trauma_categories"] = llm_res.get("trauma_categories", [])
                    result["trauma_keywords"] = llm_res.get("trauma_keywords", [])
                    result["sentiment"] = float(llm_res.get("sentiment", 0.0))
                    result["sentiment_label"] = llm_res.get("sentiment_label", "neutral")
                    result["dominant_emotion"] = llm_res.get("dominant_emotion", "neutral")
                    result["suicidal_ideation"] = llm_res.get("suicidal_ideation", {
                        "flag": False, "confidence": 0.0, "risk_level": "none", "matched_phrases": []
                    })
                    result["legal_violations"] = llm_res.get("legal_violations", [])
                    result["customized_recommendations"] = llm_res.get("recommendations", [])
                    result["llm_enhanced"] = True
                    result["durations"]["llm"] = round(time.time() - llm_start, 3)
                    logger.info("Text pipeline completed using Next-Gen LLM (%s)", self.llm.model)
                    return result
            except Exception as e:
                logger.warning("LLM analysis failed, falling back to local analyzers: %s", e)

        # ─── Fallback / Local Rule-Based Pipeline ───
        # Stage 1: Language Detection
        start = time.time()
        try:
            if not language:
                detect_result = self.lang_detector.detect_text_language(text)
                result["detected_language"] = detect_result.get("language_code", "en")
            logger.info("Language detected: %s", result["detected_language"])
        except Exception as e:
            logger.error("Language detection failed: %s", e)
        result["durations"]["lang_detect"] = round(time.time() - start, 3)

        # Stage 2: Translation to English
        start = time.time()
        try:
            detected = result["detected_language"]
            if detected and detected != "en":
                trans_result = self.translator.translate(text, source_lang=detected, target_lang="en")
                result["translated_text"] = trans_result.get("translated_text", text)
            else:
                result["translated_text"] = text
            logger.info("Translation completed")
        except Exception as e:
            logger.error("Translation failed: %s", e)
            result["translated_text"] = text
        result["durations"]["translation"] = round(time.time() - start, 3)

        analysis_text = result["translated_text"]

        # Stage 3: Trauma Keyword Analysis
        start = time.time()
        try:
            trauma_result = self.trauma.analyze(analysis_text, language="en")
            result["trauma_keywords"] = trauma_result.get("matches", [])
            result["trauma_score"] = trauma_result.get("keyword_density_score", 0.0)
            result["trauma_categories"] = trauma_result.get("categories_found", [])
            logger.info("Trauma analysis: score=%.1f, categories=%s", result["trauma_score"], result["trauma_categories"])
        except Exception as e:
            logger.error("Trauma keyword analysis failed: %s", e)
        result["durations"]["trauma"] = round(time.time() - start, 3)

        # Stage 4: Sentiment Analysis
        start = time.time()
        try:
            sent_result = self.sentiment.analyze(analysis_text)
            result["sentiment"] = sent_result.get("sentiment_score", 0.0)
            result["sentiment_label"] = sent_result.get("sentiment_label", "neutral")
            result["emotion_scores"] = sent_result.get("emotion_scores", [])
            result["dominant_emotion"] = sent_result.get("dominant_emotion", "neutral")
            logger.info("Sentiment: %.2f (%s)", result["sentiment"], result["sentiment_label"])
        except Exception as e:
            logger.error("Sentiment analysis failed: %s", e)
        result["durations"]["sentiment"] = round(time.time() - start, 3)

        # Stage 5: Suicidal Ideation Detection
        start = time.time()
        try:
            si_result_en = self.si_detector.analyze(analysis_text, language="en")
            si_result_orig = self.si_detector.analyze(text, language=result["detected_language"])

            if si_result_orig.get("confidence", 0) > si_result_en.get("confidence", 0):
                si_best = si_result_orig
            else:
                si_best = si_result_en

            all_phrases = list(set(
                si_result_en.get("matched_phrases", []) + si_result_orig.get("matched_phrases", [])
            ))

            result["suicidal_ideation"] = {
                "flag": si_best.get("flag", False) or si_result_orig.get("flag", False),
                "confidence": si_best.get("confidence", 0.0),
                "matched_phrases": all_phrases,
                "risk_level": si_best.get("risk_level", "none"),
                "recommendation": si_best.get("recommendation", ""),
            }
        except Exception as e:
            logger.error("Suicidal ideation detection failed: %s", e)
        result["durations"]["suicidal_ideation"] = round(time.time() - start, 3)

        return result
