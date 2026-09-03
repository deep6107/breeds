import os
import json
import re
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

def extract_traits_from_image(image_bytes: bytes, mime_type: str = "image/jpeg") -> dict:
    api_key = os.environ.get("GEMINI_API_KEY")
    
    if not api_key:
        print("Warning: GEMINI_API_KEY not found. Using default fallback breed.")
        return {"breed_name": "Murrah", "species": "buffalo"}
    
    try:
        client = genai.Client(api_key=api_key)
        
        prompt = """
        Analyze this image of a cattle or buffalo. Identify its exact breed name (e.g., Murrah, Gir, Sahiwal, Nili-Ravi, Tharparkar, Jafarabadi) and species (cattle or buffalo).
        Return ONLY a valid JSON object in this exact format, with no markdown formatting or extra text:
        {"breed_name": "Murrah", "species": "buffalo"}
        """
        
        response = client.models.generate_content(
            model='gemini-3.6-flash',
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
            
        match = re.search(r'\{.*?\}', text, re.DOTALL)
        if match:
            parsed = json.loads(match.group(0))
            if parsed and "breed_name" in parsed:
                return parsed
            
    except Exception as e:
        print("Vision Extraction Error:", e)

    return {"breed_name": "Murrah", "species": "buffalo"}