import logging
import os
import numpy as np
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class VoiceEmotionAnalyzer:
    """
    Classifies emotion from voice audio.
    Prototype uses MFCC heuristics via librosa.
    """
    
    def __init__(self):
        self._librosa_loaded = False
        self.emotions = ['neutral', 'happy', 'sad', 'angry', 'fearful', 'disgusted', 'surprised']
        
    def _check_deps(self):
        try:
            import librosa
            self._librosa_loaded = True
        except ImportError:
            logger.warning("librosa not installed. Emotion analysis will return defaults.")

    def analyze(self, audio_path: str) -> Dict[str, Any]:
        """
        Analyzes audio file for emotional content.
        
        Args:
            audio_path: Path to the audio file
            
        Returns:
            Dict containing emotion probabilities and dominant emotion.
        """
        result = {
            "emotions": [{"label": e, "confidence": 1.0/len(self.emotions)} for e in self.emotions],
            "dominant_emotion": "neutral"
        }
        
        if not os.path.exists(audio_path):
            logger.error(f"Audio file not found: {audio_path}")
            return result
            
        self._check_deps()
        
        if not self._librosa_loaded:
            return result
            
        try:
            import librosa
            y, sr = librosa.load(audio_path, sr=None)
            
            if len(y) == 0:
                return result
                
            # Heuristic features
            rmse = np.mean(librosa.feature.rms(y=y))
            zcr = np.mean(librosa.feature.zero_crossing_rate(y=y))
            spec_cent = np.mean(librosa.feature.spectral_centroid(y=y, sr=sr))
            
            # Simple heuristic mapping for prototype
            scores = {e: 0.1 for e in self.emotions} # baseline
            
            if rmse > 0.1 and spec_cent > 2000:
                scores['angry'] += 0.5
                scores['fearful'] += 0.3
            elif rmse < 0.02 and spec_cent < 1200:
                scores['sad'] += 0.5
                scores['neutral'] += 0.3
            elif rmse > 0.05 and zcr > 0.1:
                scores['happy'] += 0.4
                scores['surprised'] += 0.4
            else:
                scores['neutral'] += 0.6
                
            # Normalize
            total = sum(scores.values())
            norm_scores = {k: v/total for k, v in scores.items()}
            
            emotions_list = [{"label": k, "confidence": float(v)} for k, v in sorted(norm_scores.items(), key=lambda item: item[1], reverse=True)]
            
            result["emotions"] = emotions_list
            result["dominant_emotion"] = emotions_list[0]["label"]
            
        except Exception as e:
            logger.error(f"Error during voice emotion analysis: {e}")
            
        return result

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    analyzer = VoiceEmotionAnalyzer()
    # print(analyzer.analyze("test.wav"))
