import logging
import re
from typing import Dict, Any

logger = logging.getLogger(__name__)

class SuicidalIdeationDetector:
    """
    High-sensitivity detector for suicidal ideation.
    """
    
    EXPLICIT_PATTERNS = [
        r'want to die', r'kill myself', r'end my life', r'commit suicide', r'take my own life',
        r'मरना चाहता', r'आत्महत्या', r'जान दे दूँ'
    ]
    
    IMPLICIT_PATTERNS = [
        r'no reason to live', r'better off dead', r'can\'t go on', r'no hope left', 
        r'nobody cares', r'burden to everyone', r'wish i was never born', r'what\'s the point', 
        r'no way out', r'end it all'
    ]
    
    CONTEXTUAL_PATTERNS = [
        r'hopeless', r'worthless', r'trapped', r'exhausted', r'giving up', r'final goodbye', r'last wish'
    ]
    
    def __init__(self):
        pass

    def analyze(self, text: str, language: str = 'en') -> Dict[str, Any]:
        """Detects suicidal ideation patterns."""
        result = {
            "flag": False,
            "confidence": 0.0,
            "risk_level": "none",
            "matched_phrases": [],
            "recommendation": ""
        }
        
        if not text or not text.strip():
            return result
            
        text_lower = text.lower()
        
        explicit_matches = []
        for p in self.EXPLICIT_PATTERNS:
            if re.search(p, text_lower):
                explicit_matches.append({"phrase": p, "type": "explicit"})
                
        implicit_matches = []
        for p in self.IMPLICIT_PATTERNS:
            if re.search(p, text_lower):
                implicit_matches.append({"phrase": p, "type": "implicit"})
                
        contextual_matches = []
        for p in self.CONTEXTUAL_PATTERNS:
            if re.search(p, text_lower):
                contextual_matches.append({"phrase": p, "type": "contextual"})
                
        result["matched_phrases"] = explicit_matches + implicit_matches + contextual_matches
        
        if explicit_matches:
            result["flag"] = True
            result["confidence"] = 0.95
            result["risk_level"] = "imminent"
            result["recommendation"] = "IMMEDIATE ACTION REQUIRED: Escalate to emergency response team. Keep caller on the line."
        elif implicit_matches:
            result["flag"] = True
            result["confidence"] = 0.75
            result["risk_level"] = "high"
            result["recommendation"] = "HIGH RISK: Connect to specialized counselor immediately. Conduct risk assessment."
        elif len(contextual_matches) >= 2:
            result["flag"] = True
            result["confidence"] = 0.5
            result["risk_level"] = "moderate"
            result["recommendation"] = "MODERATE RISK: Counselor should explore feelings of hopelessness and screen for ideation."
            
        return result

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    detector = SuicidalIdeationDetector()
    print(detector.analyze("I just can't go on anymore, I want to die."))
