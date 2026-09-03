import os
import json
from google import genai
from google.genai import types

def extract_traits_from_image(image_bytes: bytes, mime_type: str = "image/jpeg") -> dict:
    api_key = os.environ.get("GEMINI_API_KEY")
    
    if not api_key:
        return {"breed_name": "Murrah", "species": "buffalo"}
    
    try:
        client = genai.Client(api_key=api_key)
        
        prompt = """
        Analyze this image of a cattle or buffalo. Identify its exact breed name (e.g., Murrah, Gir, Sahiwal, Nili-Ravi, Red Sindhi, Tharparkar, Jafarabadi) and species.
        Return ONLY a valid JSON object in this exact format:
        {"breed_name": "Murrah", "species": "buffalo"}
        Do not include any extra text or markdown formatting outside the JSON block.
        """
        
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=[
                types.Part.from_bytes(data=image_bytes, mime_type=mime_type or "image/jpeg"),
                prompt
            ]
        )
        
        text = response.text.strip()
        if text.startswith("```json"):
            text = text[7:-3].strip()
        elif text.startswith("```"):
            text = text[3:-3].strip()
            
        parsed = json.loads(text)
        if parsed and "breed_name" in parsed:
            return parsed
            
    except Exception as e:
        print("Vision Extraction Error:", e)

    return {"breed_name": "Murrah", "species": "buffalo"}