def calculate_matching_percentage(matched_count, total_features):
    if total_features == 0:
        return 0

    return (matched_count / total_features) * 100


def create_result_file(
    matched_features_list,
    breed_utility_list,
    total_features
):

    if not matched_features_list:
        with open("breed_result.txt", "w") as file:
            file.write("No matching breed found.\n")

        return "breed_result.txt"

    best_breed = max(
        matched_features_list,
        key=lambda x: x.get("total_matches", 0)
    )

    breed_name = best_breed.get("breed_name")
    matched_count = best_breed.get("total_matches", 0)

    percentage = calculate_matching_percentage(
        matched_count,
        total_features
    )

    winning_utility = {}

    for breed in breed_utility_list:
        if breed.get("breed_name") == breed_name:
            winning_utility = breed.get("breed_utility", {})
            break

    # "w" means WRITE/OVERWRITE.
    # It replaces the old file every time.
    with open("breed_result.txt", "w") as file:

        file.write("CATTLE / BUFFALO BREED RECOGNITION RESULT\n")
        file.write("=" * 45 + "\n\n")

        file.write(f"Breed: {breed_name}\n")
        file.write(f"Matching Features: {matched_count}\n")
        file.write(f"Total Features: {total_features}\n")
        file.write(f"Matching Percentage: {percentage:.2f}%\n\n")

        file.write("Breed Information\n")
        file.write("-" * 20 + "\n")

        for key, value in winning_utility.items():
            file.write(f"{key}: {value}\n")

    return "breed_result.txt"