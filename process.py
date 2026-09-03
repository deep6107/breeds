def calculate_matching_percentage(matched_count, total_features):
    if not total_features:
        return 0
    return (matched_count / total_features) * 100

def create_result_file(
    matched_features_list,
    breed_utility_list,
    total_features=6,
    filepath="breed.txt"
):
    if not matched_features_list:
        with open(filepath, "w", encoding="utf-8") as file:
            file.write("Breed : No matching breed found : 0%\n")
        return filepath

    # Sort breeds by total matches descending (take top 3 for tabs)
    sorted_breeds = sorted(
        matched_features_list,
        key=lambda x: x.get("total_matches", 0),
        reverse=True
    )[:3]

    best_breed = sorted_breeds[0]
    best_percentage = calculate_matching_percentage(
        best_breed.get("total_matches", 0),
        total_features
    )

    # Build breed header string: "Breed : Surti, Nagpuri, Pandharpuri : 83%"
    breed_names = [b.get("breed_name", "Unknown").capitalize() for b in sorted_breeds]
    title_string = ", ".join(breed_names)

    # Map utility details by breed name for quick lookup
    utility_map = {
        item.get("breed_name", "").lower(): item.get("breed_utility", {})
        for item in breed_utility_list
    }

    with open(filepath, "w", encoding="utf-8") as file:
        file.write(f"Breed : {title_string} : {int(best_percentage)}%\n")

        for idx, breed in enumerate(sorted_breeds, start=1):
            name = breed.get("breed_name", "Unknown").capitalize()
            details = utility_map.get(name.lower(), {})

            file.write(f"{idx}.{name}:\n")
            file.write("-" * 20 + "\n")
            file.write(f"origin: {details.get('origin', 'N/A')}\n")
            file.write(f"species: {details.get('species', 'N/A')}\n")
            file.write(f"type: {details.get('type', 'N/A')}\n")
            file.write(f"milk_fat: {details.get('milk_fat', 'N/A')}\n")
            file.write(f"known_for: {details.get('known_for', 'N/A')}\n")
            file.write(f"benefits: {details.get('benefits', 'N/A')}\n\n")

    return filepath