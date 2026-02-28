"""
Translation utilities for CodeAI Pakistan
Handles English to Urdu translation using Gemini
"""

def translate_to_urdu(text: str, gemini_model=None) -> str:
    """
    Translate English text to Urdu using Gemini API
    
    Args:
        text: English text to translate
        gemini_model: Gemini model instance
    
    Returns:
        Translated Urdu text or original text if translation fails
    """
    
    if not gemini_model or not text or not text.strip():
        return text
    
    try:
        prompt = (
            f"Translate the following text to Urdu. "
            f"Maintain technical terms in English if they don't have good Urdu equivalents. "
            f"Keep code snippets unchanged. "
            f"Return ONLY the translated text without any preamble or explanation.\n\n"
            f"Text to translate:\n{text[:3000]}"
        )
        
        response = gemini_model.generate_content(prompt)
        translated_text = getattr(response, "text", None)
        
        if not translated_text and getattr(response, "candidates", None):
            parts = getattr(response.candidates[0].content, "parts", [])
            translated_text = "".join(getattr(p, "text", "") for p in parts)
        
        if not translated_text:
            return text
        
        return translated_text.strip()
        
    except Exception as e:
        print(f"Translation error: {e}")
        return text

def translate_bug_descriptions(bugs: list, gemini_model=None) -> list:
    """
    Translate bug descriptions to Urdu
    
    Args:
        bugs: List of bug dicts with description_en field
        gemini_model: Gemini model instance
    
    Returns:
        Updated bugs list with description_ur filled
    """
    
    if not gemini_model or not bugs:
        return bugs
    
    for bug in bugs:
        if bug.get("description_en"):
            bug["description_ur"] = translate_to_urdu(
                bug["description_en"], 
                gemini_model
            )
    
    return bugs

def translate_documentation(docs: dict, gemini_model=None) -> dict:
    """
    Translate documentation from English to Urdu
    
    Args:
        docs: Dict with 'english' key
        gemini_model: Gemini model instance
    
    Returns:
        Dict with both 'english' and 'urdu' keys
    """
    
    if not gemini_model or not docs.get("english"):
        return docs
    
    docs["urdu"] = translate_to_urdu(docs["english"], gemini_model)
    
    return docs