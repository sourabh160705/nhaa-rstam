import logging
import os
import numpy as np
from typing import Dict, Any

logger = logging.getLogger(__name__)

class AcousticFeatureAnalyzer:
    """
    Analyzes acoustic features like pitch, pauses, and jitter.
    Calculates an acoustic distress score based on these features.
    """
    
    def __init__(self):
        self._librosa_loaded = False
        self._parselmouth_loaded = False
        
    def _check_deps(self):
        try:
            import librosa
            self._librosa_loaded = True
        except ImportError:
            logger.warning("librosa not installed. Acoustic analysis will be limited.")
            
        try:
            import parselmouth
            from parselmouth.praat import call
            self._parselmouth_loaded = True
        except ImportError:
            logger.warning("parselmouth not installed. Jitter/shimmer/HNR will be unavailable.")

    def analyze(self, audio_path: str) -> Dict[str, Any]:
        """
        Analyzes audio file for acoustic features.
        
        Args:
            audio_path: Path to the audio file
            
        Returns:
            Dict containing pitch, speech rate, pause statistics, and distress score.
        """
        if not os.path.exists(audio_path):
            logger.error(f"Audio file not found: {audio_path}")
            return self._empty_result()
            
        self._check_deps()
        
        result = self._empty_result()
        
        try:
            # Basic analysis with librosa
            if self._librosa_loaded:
                import librosa
                y, sr = librosa.load(audio_path, sr=None)
                
                # Check for short or empty audio
                if len(y) == 0:
                    logger.warning(f"Audio file is empty: {audio_path}")
                    return result
                
                duration = librosa.get_duration(y=y, sr=sr)
                if duration < 1.0:
                    logger.warning(f"Audio too short for meaningful analysis: {duration}s")
                
                # Pitch (F0) tracking
                f0, voiced_flag, voiced_probs = librosa.pyin(y, fmin=librosa.note_to_hz('C2'), fmax=librosa.note_to_hz('C7'))
                valid_f0 = f0[voiced_flag]
                
                if len(valid_f0) > 0:
                    result["mean_pitch"] = float(np.mean(valid_f0))
                    result["pitch_std"] = float(np.std(valid_f0))
                    result["pitch_range"] = float(np.max(valid_f0) - np.min(valid_f0))
                    
                # Pause detection (silences > 300ms)
                non_mute_intervals = librosa.effects.split(y, top_db=30)
                pauses = []
                last_end = 0
                for interval in non_mute_intervals:
                    start, end = interval
                    pause_dur = (start - last_end) / sr
                    if pause_dur > 0.3:
                        pauses.append(pause_dur)
                    last_end = end
                    
                result["pause_count"] = len(pauses)
                if pauses:
                    result["mean_pause_duration"] = float(np.mean(pauses))
                    result["total_pause_duration"] = float(np.sum(pauses))
                    
                # Speech rate (estimated syllables per sec)
                onset_env = librosa.onset.onset_strength(y=y, sr=sr)
                peaks = librosa.util.peak_pick(onset_env, pre_max=3, post_max=3, pre_avg=3, post_avg=5, delta=0.5, wait=10)
                speaking_time = duration - result["total_pause_duration"]
                if speaking_time > 0:
                    result["speech_rate"] = float(len(peaks) / speaking_time)
            
            # Praat analysis for jitter, shimmer, HNR
            if self._parselmouth_loaded:
                import parselmouth
                from parselmouth.praat import call
                sound = parselmouth.Sound(audio_path)
                pointProcess = call(sound, "To PointProcess (periodic, cc)", 75, 500)
                
                result["jitter"] = call(pointProcess, "Get jitter (local)", 0, 0, 0.0001, 0.02, 1.3) * 100
                result["shimmer"] = call([sound, pointProcess], "Get shimmer (local)", 0, 0, 0.0001, 0.02, 1.3, 1.6) * 100
                harmonicity = call(sound, "To Harmonicity (cc)", 0.01, 75, 0.1, 1.0)
                result["hnr"] = call(harmonicity, "Get mean", 0, 0)
                
            result["acoustic_distress_score"] = self._calculate_distress(result)
            
        except Exception as e:
            logger.error(f"Error during acoustic analysis: {e}")
            
        return result
        
    def _empty_result(self) -> Dict[str, Any]:
        return {
            "mean_pitch": 0.0, "pitch_std": 0.0, "pitch_range": 0.0,
            "speech_rate": 0.0,
            "pause_count": 0, "mean_pause_duration": 0.0, "total_pause_duration": 0.0,
            "jitter": 0.0, "shimmer": 0.0, "hnr": 0.0,
            "acoustic_distress_score": 0.0
        }
        
    def _calculate_distress(self, features: Dict[str, Any]) -> float:
        score = 0.0
        
        # High pitch variability
        if features["pitch_std"] > 50:
            score += 20
        # Slow speech rate (indicative of depression/distress)
        if 0 < features["speech_rate"] < 2.5:
            score += 20
        # High pause duration
        if features["total_pause_duration"] > 5:
            score += 20
        # High jitter
        if features["jitter"] and features["jitter"] > 2.0:
            score += 20
        # Low HNR (hoarse/breathy voice)
        if features["hnr"] and features["hnr"] < 15.0:
            score += 20
            
        return min(100.0, score)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    analyzer = AcousticFeatureAnalyzer()
    # print(analyzer.analyze("test.wav"))
