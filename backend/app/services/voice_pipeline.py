"""Voice analysis orchestration pipeline.

Coordinates speech-to-text, acoustic feature extraction, and voice emotion
detection to produce a comprehensive voice analysis result.
"""
import time
import logging
from typing import Optional

from ..analyzers.speech_to_text import SpeechToTextAnalyzer
from ..analyzers.acoustic_features import AcousticFeatureAnalyzer
from ..analyzers.voice_emotion import VoiceEmotionAnalyzer

logger = logging.getLogger(__name__)


class VoicePipeline:
    """Orchestrates voice analysis through multiple analyzer stages."""

    def __init__(self):
        self.stt = SpeechToTextAnalyzer()
        self.acoustic = AcousticFeatureAnalyzer()
        self.emotion = VoiceEmotionAnalyzer()

    async def process(self, audio_path: str, language: Optional[str] = None) -> dict:
        """Process an audio file through the full voice analysis pipeline.

        Args:
            audio_path: Path to the audio file.
            language: Optional language code hint.

        Returns:
            dict with transcript, detected_language, acoustic features,
            voice emotion distribution, and stage durations.
        """
        result = {
            "transcript": "",
            "detected_language": language or "en",
            "acoustic_features": None,
            "acoustic_distress": 0.0,
            "voice_emotion": {},
            "dominant_emotion": "neutral",
            "segments": [],
            "durations": {},
        }

        # Stage 1: Speech-to-Text
        start = time.time()
        try:
            stt_result = self.stt.transcribe(audio_path, language=language)
            result["transcript"] = stt_result.get("transcript", "")
            result["detected_language"] = stt_result.get("detected_language", language or "en")
            result["segments"] = stt_result.get("segments", [])
            logger.info("STT completed: %d chars transcribed", len(result["transcript"]))
        except Exception as e:
            logger.error("Speech-to-text failed: %s", e)
        result["durations"]["stt"] = round(time.time() - start, 3)

        # Stage 2: Acoustic Feature Analysis
        start = time.time()
        try:
            acoustic_result = self.acoustic.analyze(audio_path)
            result["acoustic_features"] = acoustic_result
            result["acoustic_distress"] = acoustic_result.get("acoustic_distress_score", 0.0)
            logger.info("Acoustic analysis completed: distress=%.1f", result["acoustic_distress"])
        except Exception as e:
            logger.error("Acoustic feature analysis failed: %s", e)
        result["durations"]["acoustic"] = round(time.time() - start, 3)

        # Stage 3: Voice Emotion Detection
        start = time.time()
        try:
            emotion_result = self.emotion.analyze(audio_path)
            emotions = emotion_result.get("emotions", [])
            # Convert list of {label, confidence} to dict
            emotion_dict = {}
            for em in emotions:
                emotion_dict[em["label"]] = em["confidence"]
            result["voice_emotion"] = emotion_dict
            result["dominant_emotion"] = emotion_result.get("dominant_emotion", "neutral")
            logger.info("Voice emotion completed: dominant=%s", result["dominant_emotion"])
        except Exception as e:
            logger.error("Voice emotion analysis failed: %s", e)
        result["durations"]["voice_emotion"] = round(time.time() - start, 3)

        return result
