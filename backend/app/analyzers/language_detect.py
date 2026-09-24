import logging
import os
from typing import Dict, Any

logger = logging.getLogger(__name__)

class LanguageDetector:
    """
    Detects language from text or audio.
    """
    
    SUPPORTED_LANGUAGES = {
        'en': 'English', 'hi': 'Hindi', 'ta': 'Tamil', 'te': 'Telugu',
        'mr': 'Marathi', 'bn': 'Bengali', 'kn': 'Kannada', 'gu': 'Gujarati',
        'ml': 'Malayalam', 'pa': 'Punjabi', 'or': 'Odia', 'ur': 'Urdu'
    }
    
    def __init__(self):
        self._whisper_model = None
        
    def detect_text_language(self, text: str) -> Dict[str, Any]:
        """Detects language from text using langdetect."""
        if not text or not text.strip():
            return {"language_code": "unknown", "language_name": "Unknown", "confidence": 0.0}
            
        try:
            import langdetect
            from langdetect import detect_langs
            
            langs = detect_langs(text)
            if not langs:
                return {"language_code": "unknown", "language_name": "Unknown", "confidence": 0.0}
                
            best_match = langs[0]
            lang_code = best_match.lang
            
            if lang_code in self.SUPPORTED_LANGUAGES:
                return {
                    "language_code": lang_code,
                    "language_name": self.SUPPORTED_LANGUAGES[lang_code],
                    "confidence": float(best_match.prob)
                }
            else:
                return {
                    "language_code": lang_code,
                    "language_name": "Unsupported/Unknown",
                    "confidence": float(best_match.prob)
                }
                
        except ImportError:
            logger.error("langdetect not installed.")
        except Exception as e:
            logger.error(f"Error detecting text language: {e}")
            
        return {"language_code": "unknown", "language_name": "Unknown", "confidence": 0.0}

    def detect_audio_language(self, audio_path: str) -> Dict[str, Any]:
        """Detects language from audio using Whisper."""
        if not os.path.exists(audio_path):
            return {"language_code": "unknown", "language_name": "Unknown", "confidence": 0.0}
            
        try:
            if self._whisper_model is None:
                import whisper
                self._whisper_model = whisper.load_model("base")
                
            audio = whisper.load_audio(audio_path)
            audio = whisper.pad_or_trim(audio)
            mel = whisper.log_mel_spectrogram(audio).to(self._whisper_model.device)
            
            _, probs = self._whisper_model.detect_language(mel)
            lang_code = max(probs, key=probs.get)
            
            if lang_code in self.SUPPORTED_LANGUAGES:
                return {
                    "language_code": lang_code,
                    "language_name": self.SUPPORTED_LANGUAGES[lang_code],
                    "confidence": float(probs[lang_code])
                }
            else:
                return {
                    "language_code": lang_code,
                    "language_name": "Unsupported/Unknown",
                    "confidence": float(probs[lang_code])
                }
                
        except Exception as e:
            logger.error(f"Error detecting audio language: {e}")
            
        return {"language_code": "unknown", "language_name": "Unknown", "confidence": 0.0}

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    detector = LanguageDetector()
    print(detector.detect_text_language("This is a test."))
