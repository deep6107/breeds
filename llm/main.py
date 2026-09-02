import sys
import subprocess
import json

def process_cattle_image(image_path: str) -> dict:
    # STEP 1: Extract features
    try:
        subprocess.run(
            [sys.executable, "feature_extractor.py", image_path],
            check=True,
            capture_output=True,
            text=True
        )
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Feature extraction failed: {e.stderr}") from e

    # STEP 2: Predict breed
    try:
        subprocess.run(
            [sys.executable, "breed_classifier.py"],
            check=True,
            capture_output=True,
            text=True
        )
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Breed classification failed: {e.stderr}") from e

    # STEP 3: Create and return final filtered result
    try:
        with open("breed_result.json", "r") as f:
            breed_result = json.load(f)

        features = breed_result.get("Extracted_Features", {})

        final_result = {
            "colour": features.get("Coat_Color", ""),
            "hump": features.get("Hump", ""),
            "ears": features.get("Ears", ""),
            "forehead": features.get("Forehead", ""),
            "horns": features.get("Horns", ""),
            "size": features.get("Body_Size", "")
        }

        # Optional: Save the final JSON to a file if other scripts still need it
        with open("final_result.json", "w") as f:
            json.dump(final_result, f, indent=4)

        return final_result

    except FileNotFoundError:
        raise FileNotFoundError("breed_result.json was not found. Ensure breed_classifier.py generates it.")
    except json.JSONDecodeError:
        raise ValueError("breed_result.json contains invalid JSON.")
    except Exception as e:
        raise RuntimeError(f"Unexpected error creating final result: {e}")