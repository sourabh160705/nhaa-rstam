import logging
import re
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class TraumaKeywordAnalyzer:
    """
    Detects trauma-related keywords across multiple categories.
    """
    
    LEXICON = {
        "VIOLENCE": {
            "severity": 5,
            "keywords": ["murder", "murdered", "killed", "kill", "beaten", "beat", "beating", "assault", "assaulted", "rape", "raped", "gang rape", "acid attack", "burning", "burned", "burnt", "stabbing", "stabbed", "lynching", "lynched", "mob violence", "attack", "attacked", "हत्या", "मारा", "पीटा", "बलात्कार"]
        },
        "DISCRIMINATION": {
            "severity": 4,
            "keywords": ["untouchability", "boycott", "boycotted", "denied entry", "humiliation", "humiliated", "caste slur", "forced labor", "bonded labor", "manual scavenging", "discrimination", "discriminated", "छुआछूत", "बहिष्कार", "अपमान"]
        },
        "THREATS": {
            "severity": 4,
            "keywords": ["death threat", "life threat", "threaten", "threatened", "threatening", "intimidation", "intimidated", "blackmail", "blackmailed", "extortion", "land grab", "property destruction", "arson", "धमकी", "जान से मारने की धमकी"]
        },
        "PSYCHOLOGICAL": {
            "severity": 3,
            "keywords": ["fear", "terrified", "helpless", "hopeless", "no way out", "cannot sleep", "nightmares", "crying", "breakdown", "depression", "anxiety", "panic", "डर", "रो रही", "तनाव"]
        },
        "SUICIDAL": {
            "severity": 5,
            "keywords": ["want to die", "end my life", "suicide", "kill myself", "no reason to live", "better off dead", "cannot take it anymore", "आत्महत्या", "मरना चाहता हूँ", "जान देना"]
        },
        "LEGAL": {
            "severity": 2,
            "keywords": ["FIR not filed", "police refused", "case delayed", "evidence destroyed", "witness threatened", "false case", "wrongful arrest", "एफआईआर नहीं"]
        },
        "DISPLACEMENT": {
            "severity": 3,
            "keywords": ["driven out", "forced to leave", "homeless", "displaced", "refugee", "shelter needed", "nowhere to go", "बेघर", "निकाल दिया"]
        }
    }
    
    def __init__(self):
        pass

    def analyze(self, text: str, language: str = 'en') -> Dict[str, Any]:
        """Analyzes text for trauma keywords."""
        result = {
            "matches": [],
            "keyword_density_score": 0.0,
            "categories_found": []
        }
        
        if not text or not text.strip():
            return result
            
        lower_text = text.lower()
        matched_categories = set()
        total_score = 0
        word_count = max(1, len(lower_text.split()))
        
        for category, data in self.LEXICON.items():
            severity = data["severity"]
            for keyword in data["keywords"]:
                keyword_lower = keyword.lower()
                
                # Word boundary search if it's alphanumeric
                if keyword_lower.isalnum():
                    pattern = r'\b' + re.escape(keyword_lower) + r'\b'
                else:
                    pattern = re.escape(keyword_lower)
                    
                for match in re.finditer(pattern, lower_text):
                    start = max(0, match.start() - 25)
                    end = min(len(text), match.end() + 25)
                    snippet = text[start:end].replace('\n', ' ')
                    
                    result["matches"].append({
                        "keyword": keyword,
                        "category": category,
                        "severity": severity,
                        "context_snippet": f"...{snippet}..."
                    })
                    matched_categories.add(category)
                    total_score += severity
                    
        result["categories_found"] = list(matched_categories)

        # Score based on:
        # - Number of distinct categories hit (breadth of trauma)
        # - Total severity points (intensity)
        # - Proportion of text that is trauma-related (density)
        num_matches = len(result["matches"])
        category_count = len(matched_categories)

        # Base score from severity accumulation (capped at 60)
        severity_component = min(60.0, total_score * 4.0)
        # Category breadth bonus: more categories = worse (up to 25)
        breadth_component = min(25.0, category_count * 5.0)
        # Density: ratio of matches to word count (up to 15)
        density_ratio = num_matches / word_count
        density_component = min(15.0, density_ratio * 100.0)

        density = min(100.0, severity_component + breadth_component + density_component)
        result["keyword_density_score"] = round(float(density), 2)
        
        return result

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    analyzer = TraumaKeywordAnalyzer()
    print(analyzer.analyze("They gave me a death threat and I want to die."))
