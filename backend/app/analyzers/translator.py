import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class TextTranslator:
    """
    Translates text to English using Helsinki-NLP MarianMT models.
    """
    
    def __init__(self):
        self.models = {}
        self.tokenizers = {}
        
    def _get_model_name(self, source_lang: str, target_lang: str) -> str:
        # Mapping ISO 639-1 to Helsinki model names where available
        # Some Indian languages might not have direct src-en models, this is a prototype fallback
        return f"Helsinki-NLP/opus-mt-{source_lang}-{target_lang}"

    def translate(self, text: str, source_lang: str, target_lang: str = 'en') -> Dict[str, Any]:
        """Translates text from source to target language."""
        result = {
            "original_text": text,
            "translated_text": text,
            "source_lang": source_lang,
            "target_lang": target_lang,
            "translation_successful": False
        }
        
        if not text or not text.strip():
            return result
            
        if source_lang == target_lang:
            result["translation_successful"] = True
            return result
            
        try:
            from transformers import MarianMTModel, MarianTokenizer
            
            model_name = self._get_model_name(source_lang, target_lang)
            
            if model_name not in self.models:
                logger.info(f"Loading translation model: {model_name}")
                self.tokenizers[model_name] = MarianTokenizer.from_pretrained(model_name)
                self.models[model_name] = MarianMTModel.from_pretrained(model_name)
                
            tokenizer = self.tokenizers[model_name]
            model = self.models[model_name]
            
            inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True)
            translated_ids = model.generate(**inputs)
            translated_text = tokenizer.batch_decode(translated_ids, skip_special_tokens=True)[0]
            
            result["translated_text"] = translated_text
            result["translation_successful"] = True
            
        except ImportError:
            logger.error("transformers not installed. Skipping translation.")
        except Exception as e:
            logger.warning(f"Translation failed for {source_lang}->{target_lang}: {e}. Returning original text.")
            
        return result

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    translator = TextTranslator()
    # print(translator.translate("नमस्ते", "hi", "en"))
