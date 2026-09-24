import re

class PIIAnonymizer:
    def __init__(self):
        # Basic patterns
        self.patterns = {
            "PHONE": r"(\+91[\-\s]?)?[6-9]\d{9}",
            "AADHAAR": r"\b\d{4}[\-\s]?\d{4}[\-\s]?\d{4}\b",
            "EMAIL": r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+",
            "NAME": r"\b[A-Z][a-z]+ [A-Z][a-z]+\b"  # Simplistic NER
        }

    def anonymize(self, text: str) -> dict:
        anonymized_text = text
        redactions = []
        
        for pii_type, pattern in self.patterns.items():
            for match in re.finditer(pattern, text):
                original = match.group()
                replacement = f"[{pii_type}_REDACTED]"
                
                # We do string replace for simplicity here, though tracking positions needs care
                redactions.append({
                    "type": pii_type,
                    "original_length": len(original),
                    "position": match.start()
                })
                
        for pii_type, pattern in self.patterns.items():
            anonymized_text = re.sub(pattern, f"[{pii_type}_REDACTED]", anonymized_text)
                
        return {
            "anonymized_text": anonymized_text,
            "redactions": redactions
        }
