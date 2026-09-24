import os
from ..models.enums import Language

def validate_audio_file(file_path: str, max_size_mb: int = 50) -> dict:
    if not os.path.exists(file_path):
        return {"valid": False, "error": "File does not exist"}
        
    ext = os.path.splitext(file_path)[1].lower()
    valid_exts = [".wav", ".mp3", ".ogg", ".flac"]
    if ext not in valid_exts:
        return {"valid": False, "error": f"Invalid audio format. Allowed: {', '.join(valid_exts)}"}
        
    size_mb = os.path.getsize(file_path) / (1024 * 1024)
    if size_mb > max_size_mb:
        return {"valid": False, "error": f"File too large. Max size is {max_size_mb} MB"}
        
    return {"valid": True}

def validate_text_input(text: str, min_length: int = 10, max_length: int = 50000) -> dict:
    if not text:
        return {"valid": False, "error": "Text is empty"}
        
    if len(text) < min_length:
        return {"valid": False, "error": f"Text too short. Min length is {min_length}"}
        
    if len(text) > max_length:
        return {"valid": False, "error": f"Text too long. Max length is {max_length}"}
        
    return {"valid": True}

def validate_language_code(code: str) -> bool:
    try:
        Language(code)
        return True
    except ValueError:
        return False
