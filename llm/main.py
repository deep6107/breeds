import sys
import subprocess
import json

if len(sys.argv) != 2:
    print("Usage: python main.py <image_path>")
    print("Example: python main.py images/test.jpg")
    sys.exit(1)

image_path = sys.argv[1]

print("\n==============================")
print("   CATTLE BREED AI")
print("==============================")
print(f"Image: {image_path}\n")

# STEP 1: Extract features
print("Step 1: Extracting features...\n")

result = subprocess.run(
    [sys.executable, "feature_extractor.py", image_path]
)

if result.returncode != 0:
    print("\nFeature extraction failed.")
    sys.exit(1)

# STEP 2: Predict breed
print("\nStep 2: Predicting breed...\n")

result = subprocess.run(
    [sys.executable, "breed_classifier.py"]
)

if result.returncode != 0:
    print("\nBreed classification failed.")
    sys.exit(1)

print("\n==============================")
print("       PROCESS COMPLETE")
print("==============================")

# STEP 3: Create final filtered result
import json

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

    with open("final_result.json", "w") as f:
        json.dump(final_result, f, indent=4)

    print("\nFinal Output:")
    print(json.dumps(final_result, indent=4))

except Exception as e:
    print("Could not create final result:", e)