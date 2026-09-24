import logging
import os
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class SpeechToTextAnalyzer:
    """
    Whisper-based Automatic Speech Recognition (ASR) module.
    Lazy-loads the Whisper model on first use.
    """
    
    def __init__(self, model_size: str = "base"):
        self.model_size = model_size
        self._model = None
        self.supported_formats = {".wav", ".mp3", ".ogg"}
        
    def _load_model(self):
        if self._model is None:
            logger.info(f"Loading Whisper model: {self.model_size}...")
            try:
                import whisper
                self._model = whisper.load_model(self.model_size)
                logger.info("Whisper model loaded successfully.")
            except ImportError:
                logger.error("Failed to import whisper. Is openai-whisper installed?")
                raise
                
    def transcribe(self, audio_path: str, language: Optional[str] = None) -> Dict[str, Any]:
        """
        Transcribes audio file to text.
        
        Args:
            audio_path (str): Path to audio file
            language (str, optional): Target language code
            
        Returns:
            dict: Transcription result containing transcript, detected_language, and segments
        """
        if not os.path.exists(audio_path):
            logger.error(f"Audio file not found: {audio_path}")
            return {"error": "File not found", "transcript": "", "detected_language": "", "segments": []}
            
        ext = os.path.splitext(audio_path)[1].lower()
        if ext not in self.supported_formats:
            logger.warning(f"Unsupported audio format: {ext}. Attempting to process anyway.")
            
        try:
            self._load_model()
            options = {}
            if language:
                options["language"] = language
                
            logger.debug(f"Transcribing audio: {audio_path}")
            result = self._model.transcribe(audio_path, **options)
            
            return {
                "transcript": result.get("text", "").strip(),
                "detected_language": result.get("language", ""),
                "segments": [
                    {
                        "start": seg.get("start", 0.0),
                        "end": seg.get("end", 0.0),
                        "text": seg.get("text", "").strip()
                    }
                    for seg in result.get("segments", [])
                ]
            }
        except Exception as e:
            logger.error(f"Error transcribing audio {audio_path}: {e}")
            return {"error": str(e), "transcript": "", "detected_language": "", "segments": []}

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    analyzer = SpeechToTextAnalyzer("tiny")  # Use tiny for quick test
    # res = analyzer.transcribe("test.wav")
    # print(res)
