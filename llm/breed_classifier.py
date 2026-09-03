import json

# Load extracted features
with open("output.json", "r") as f:
    features = json.load(f)

animal_type = features.get("Animal_Type", "").lower()

# First classify cattle vs buffalo
if "buffalo" in animal_type:
    print("\nAnimal Type: BUFFALO")

    # Buffalo breed rules
    horns = features.get("Horns", "").lower()
    body = features.get("Body_Shape", "").lower()
    face = features.get("Face_Shape", "").lower()

    if "crescent" in horns or "curved" in horns:
        breed = "Murrah"

    elif "large" in horns and "robust" in body:
        breed = "Jaffarabadi"

    else:
        breed = "Buffalo - Breed uncertain"

else:
    print("\nAnimal Type: CATTLE")

    forehead = features.get("Forehead", "").lower()
    hump = features.get("Hump", "").lower()
    ears = features.get("Ears", "").lower()
    face = features.get("Face_Shape", "").lower()
    coat = features.get("Coat_Color", "").lower()

    # Cattle breed rules
    if "prominent" in hump and "broad" in forehead:
        breed = "Gir"

    elif "convex" in forehead or "long" in face:
        breed = "Sahiwal"

    elif "red" in coat or "reddish" in coat:
        breed = "Red Sindhi"

    elif "large" in ears and "black" in coat:
        breed = "Kankrej"

    else:
        breed = "Cattle - Breed uncertain"


# Save prediction
result = {
    "Animal_Type": features.get("Animal_Type"),
    "Predicted_Breed": breed,
    "Extracted_Features": features
}

with open("breed_result.json", "w") as f:
    json.dump(result, f, indent=4)