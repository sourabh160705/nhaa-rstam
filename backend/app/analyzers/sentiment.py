import logging
import re
from typing import Dict, Any

logger = logging.getLogger(__name__)

class TextSentimentAnalyzer:
    """
    Rule-based sentiment and emotion analyzer with proportional scoring.
    Produces varied scores based on the intensity and quantity of emotional words.
    """

    POSITIVE_WORDS = {
        'safe': 0.3, 'justice': 0.5, 'helped': 0.4, 'relieved': 0.6, 'good': 0.3,
        'hope': 0.5, 'better': 0.4, 'resolved': 0.6, 'support': 0.4, 'protected': 0.5,
        'grateful': 0.6, 'thankful': 0.5, 'improved': 0.4, 'happy': 0.6, 'peaceful': 0.7,
        'kind': 0.3, 'trust': 0.4, 'comfort': 0.5, 'confident': 0.5, 'strong': 0.4,
    }

    NEGATIVE_WORDS = {
        'bad': 0.3, 'scared': 0.6, 'hurt': 0.5, 'pain': 0.5, 'angry': 0.5,
        'sad': 0.4, 'denied': 0.4, 'attack': 0.7, 'abuse': 0.8, 'trauma': 0.7,
        'fear': 0.6, 'cry': 0.4, 'terrified': 0.8, 'hopeless': 0.8, 'helpless': 0.7,
        'suffering': 0.7, 'threat': 0.6, 'threatened': 0.7, 'beaten': 0.8, 'killed': 0.9,
        'murder': 1.0, 'rape': 1.0, 'violence': 0.8, 'harassed': 0.6, 'humiliated': 0.7,
        'desperate': 0.7, 'isolated': 0.5, 'depressed': 0.7, 'anxious': 0.5,
        'panic': 0.7, 'nightmare': 0.6, 'torment': 0.8, 'agony': 0.8,
        'distress': 0.6, 'miserable': 0.6, 'horrible': 0.6, 'terrible': 0.6,
        'worst': 0.5, 'die': 0.9, 'death': 0.8, 'afraid': 0.6, 'worried': 0.4,
        'upset': 0.4, 'broken': 0.5, 'devastated': 0.8, 'tortured': 0.9,
        'displaced': 0.5, 'boycott': 0.5, 'intimidation': 0.6, 'discrimination': 0.6,
        'injustice': 0.6, 'oppressed': 0.7, 'abandoned': 0.6, 'neglected': 0.5,
        'victimized': 0.7, 'lynching': 1.0, 'stabbing': 0.9, 'burning': 0.8,
        'arson': 0.7, 'extortion': 0.6, 'blackmail': 0.6,
    }

    # Words that map to specific emotions
    FEAR_WORDS = {'scared', 'terrified', 'afraid', 'fear', 'panic', 'threatened', 'intimidation', 'threat'}
    ANGER_WORDS = {'angry', 'furious', 'injustice', 'oppressed', 'harassed', 'discrimination'}
    SADNESS_WORDS = {'sad', 'hopeless', 'helpless', 'cry', 'depressed', 'broken', 'devastated', 'miserable', 'abandoned'}
    DISGUST_WORDS = {'disgusted', 'horrible', 'terrible', 'abuse', 'humiliated', 'victimized'}

    def __init__(self):
        pass

    def analyze(self, text: str) -> Dict[str, Any]:
        """Analyzes sentiment and emotions from text with intensity-weighted scoring."""
        result = {
            "sentiment_score": 0.0,
            "sentiment_label": "neutral",
            "emotion_scores": [
                {"label": "joy", "confidence": 0.0},
                {"label": "sadness", "confidence": 0.0},
                {"label": "anger", "confidence": 0.0},
                {"label": "fear", "confidence": 0.0},
                {"label": "surprise", "confidence": 0.0},
                {"label": "disgust", "confidence": 0.0}
            ],
            "dominant_emotion": "neutral"
        }

        if not text or not text.strip():
            return result

        words = re.findall(r'\b\w+\b', text.lower())
        unique_words = set(words)
        word_count = max(1, len(words))

        # Calculate intensity-weighted scores
        pos_intensity = sum(self.POSITIVE_WORDS[w] for w in unique_words if w in self.POSITIVE_WORDS)
        neg_intensity = sum(self.NEGATIVE_WORDS[w] for w in unique_words if w in self.NEGATIVE_WORDS)

        pos_count = len(unique_words.intersection(self.POSITIVE_WORDS))
        neg_count = len(unique_words.intersection(self.NEGATIVE_WORDS))

        # Weighted sentiment: combine intensity and proportion
        total_intensity = pos_intensity + neg_intensity
        if total_intensity > 0:
            # Score from -1 to 1, weighted by intensity
            score = (pos_intensity - neg_intensity) / total_intensity
            # Dampen slightly based on word coverage (more emotional words = more extreme)
            coverage = min(1.0, (pos_count + neg_count) / max(1, word_count) * 5)
            score = score * (0.5 + 0.5 * coverage)
        else:
            score = 0.0

        result["sentiment_score"] = round(float(score), 4)

        if score > 0.5:
            result["sentiment_label"] = "very_positive"
        elif score > 0.15:
            result["sentiment_label"] = "positive"
        elif score < -0.5:
            result["sentiment_label"] = "very_negative"
        elif score < -0.15:
            result["sentiment_label"] = "negative"

        # Emotion analysis — proportional to matching words
        fear_count = len(unique_words.intersection(self.FEAR_WORDS))
        anger_count = len(unique_words.intersection(self.ANGER_WORDS))
        sadness_count = len(unique_words.intersection(self.SADNESS_WORDS))
        disgust_count = len(unique_words.intersection(self.DISGUST_WORDS))

        total_emo = max(1, fear_count + anger_count + sadness_count + disgust_count + pos_count)

        if neg_count > 0 or pos_count > 0:
            result["emotion_scores"][0]["confidence"] = round(pos_count / total_emo, 3)      # joy
            result["emotion_scores"][1]["confidence"] = round(sadness_count / total_emo, 3)   # sadness
            result["emotion_scores"][2]["confidence"] = round(anger_count / total_emo, 3)     # anger
            result["emotion_scores"][3]["confidence"] = round(fear_count / total_emo, 3)      # fear
            result["emotion_scores"][4]["confidence"] = 0.0                                    # surprise
            result["emotion_scores"][5]["confidence"] = round(disgust_count / total_emo, 3)   # disgust

            # Find dominant emotion
            max_score = 0
            for emo in result["emotion_scores"]:
                if emo["confidence"] > max_score:
                    max_score = emo["confidence"]
                    result["dominant_emotion"] = emo["label"]

        return result


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    analyzer = TextSentimentAnalyzer()
    # Test with different inputs — should give different scores
    tests = [
        "I am very scared and in pain.",
        "They killed my brother and threatened to kill me too.",
        "I feel safe now. The police helped me. Justice was served.",
        "I was beaten and humiliated in front of the village. Nobody helped.",
        "Need information about filing an FIR.",
    ]
    for t in tests:
        r = analyzer.analyze(t)
        print(f"  [{r['sentiment_score']:+.3f} {r['sentiment_label']:>15}] {r['dominant_emotion']:>8} | {t}")
