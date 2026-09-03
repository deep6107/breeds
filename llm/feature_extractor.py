import os
import sys
import json
import time

from google import genai
from google.genai import types
from PIL import Image


# -----------------------------
# SETTINGS
# -----------------------------

MODEL = "gemini-2.5-flash"

FEATURES = [
    "Animal_Type",
    "Forehead",
    "Hump",
    "Ears",
    "Horns",
    "Face_Shape",
    "Muzzle",
    "Coat_Color",
    "Body_Size",
    "Body_Shape",
    "Legs",
    "Tail",
    "Dewlap",
    "Back"
]


# -----------------------------
# CHECK IMAGE PATH
# -----------------------------

if len(sys.argv) < 2:
    print("ERROR: Please provide an image path.")
    print("Example:")
    print("python feature_extractor.py images/test.jpg")
    sys.exit(1)

image_path = sys.argv[1]

if not os.path.exists(image_path):
    print(f"ERROR: Image not found: {image_path}")
    sys.exit(1)


# -----------------------------
# CHECK API KEY
# -----------------------------

api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    print("ERROR: GEMINI_API_KEY is not set.")
    print("Set the API key in your terminal and try again.")
    sys.exit(1)


# -----------------------------
# CREATE CLIENT
# -----------------------------

client = genai.Client(api_key=api_key)


# -----------------------------
# OPEN IMAGE
# -----------------------------

try:
    image = Image.open(image_path)
except Exception as e:
    print("ERROR: Could not open image.")
    print(e)
    sys.exit(1)


# -----------------------------
# PROMPT
# -----------------------------

prompt = f"""
You are a livestock image analysis system.

Analyze ONLY the visible physical characteristics of the animal in the image.

First determine whether the animal is:
- Cattle
- Buffalo
- Unknown

Do NOT guess a breed.

For every feature, describe only what is visibly present.
If a feature cannot be seen clearly, use "Not visible".

Return ONLY valid JSON.

The JSON must contain exactly these keys:

{json.dumps(FEATURES, indent=2)}

Important:
- Do not add extra keys.
- Do not explain your answer.
- Do not identify the breed.
- Do not guess hidden features.
"""


# -----------------------------
# CALL GEMINI
# -----------------------------

response = None

for attempt in range(3):

    try:
        print(f"Analyzing image... Attempt {attempt + 1}/3")

        response = client.models.generate_content(
            model=MODEL,
            contents=[prompt, image],
            config=types.GenerateContentConfig(
                temperature=0,
                response_mime_type="application/json"
            )
        )

        break

    except Exception as e:

        error_text = str(e)

        if "503" in error_text or "UNAVAILABLE" in error_text:

            if attempt < 2:
                print("Gemini is temporarily unavailable.")
                print("Retrying in 5 seconds...")
                time.sleep(5)
            else:
                print("ERROR: Gemini remained unavailable after 3 attempts.")
                print("Try again after a few minutes.")

        else:
            print("ERROR while contacting Gemini:")
            print(error_text)
            sys.exit(1)


if response is None:
    sys.exit(1)


# -----------------------------
# CLEAN RESPONSE
# -----------------------------

try:

    text = response.text.strip()

    # Remove markdown JSON fences if Gemini adds them
    if text.startswith("```"):
        text = text.replace("```json", "")
        text = text.replace("```", "")
        text = text.strip()

    data = json.loads(text)

except Exception as e:

    print("ERROR: Gemini did not return valid JSON.")
    print("Raw response:")
    print(response.text)
    print(e)
    sys.exit(1)


# -----------------------------
# SAVE RESULT
# -----------------------------

with open("output.json", "w", encoding="utf-8") as file:
    json.dump(data, file, indent=4, ensure_ascii=False)


# ------------------------
# DISPLAY RESULT
# ------------------------

# Do not display all extracted features here.
# The final output is handled by main.py.