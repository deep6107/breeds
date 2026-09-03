import os
from supabase import create_client, Client

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key) if url and key else None

def process_breed_detection(input_data: dict):
    if not supabase:
        return [], []

    matched_features_list = []
    breed_utility_list = []

    try:
        target_breed = input_data.get("breed_name", "").strip()
        input_colour = input_data.get("colour", "").strip().lower()
        
        is_manual_input = input_colour or any(k in input_data and input_data[k] for k in ["hump", "forehead", "horns", "ears", "size"])

        rows = []

        if target_breed and not is_manual_input:
            # Flow 1: AI Image Recognition -> Show ONLY the recognized breed
            response = supabase.table("breed_features").select("*").ilike("breed_name", f"%{target_breed}%").execute()
            rows = response.data or []
        else:
            # Flow 2: Manual input -> Show all matching breeds with strict colour check
            response = supabase.table("breed_features").select("*").execute()
            all_rows = response.data or []

            filtered_rows = []
            for row in all_rows:
                if input_colour:
                    row_colour = str(row.get("colour", "") or row.get("color", "")).strip().lower()
                    if row_colour and row_colour != "n/a":
                        if input_colour not in row_colour and row_colour not in input_colour:
                            continue

                match_other = True
                for k, val in input_data.items():
                    if k not in ["breed_name", "species", "colour"] and val:
                        row_val = str(row.get(k, "")).strip().lower()
                        if row_val and row_val != "n/a" and val.lower().strip() not in row_val:
                            match_other = False
                            break
                if match_other:
                    filtered_rows.append(row)

            rows = filtered_rows

        if not rows:
            response = supabase.table("breed_features").select("*").limit(5).execute()
            rows = response.data or []

        for row in rows:
            b_name = row.get("breed_name") or row.get("name") or "Unknown"

            # Default utility mapping from feature row
            utility_dict = {
                "origin": str(row.get("origin", "N/A")),
                "type": str(row.get("type", "N/A")),
                "milk_fat": str(row.get("milk_fat", "N/A")),
                "known_for": str(row.get("known_for", "N/A")),
                "benefits": str(row.get("benefits", "N/A"))
            }

            # Explicitly query the 'breed_utility' table to fetch specific utility records
            try:
                util_response = supabase.table("breed_utility").select("*").ilike("breed_name", f"%{b_name.strip()}%").execute()
                if util_response.data:
                    u_row = util_response.data[0]
                    utility_dict = {
                        "origin": str(u_row.get("origin") or row.get("origin") or "N/A"),
                        "type": str(u_row.get("type") or row.get("type") or "N/A"),
                        "milk_fat": str(u_row.get("milk_fat") or row.get("milk_fat") or "N/A"),
                        "known_for": str(u_row.get("known_for") or row.get("known_for") or "N/A"),
                        "benefits": str(u_row.get("benefits") or row.get("benefits") or "N/A")
                    }
            except Exception as util_err:
                print(f"breed_utility table query note for {b_name}:", util_err)

            traits_dict = {
                "species": str(row.get("species", input_data.get("species", "Cattle"))),
                "colour": str(row.get("colour") or row.get("color") or "N/A"),
                "hump": str(row.get("hump", "N/A")),
                "forehead": str(row.get("forehead", "N/A")),
                "horns": str(row.get("horns", "N/A")),
                "ears": str(row.get("ears", "N/A")),
                "size": str(row.get("size", "N/A"))
            }

            matched_features_list.append({
                "breed_name": b_name,
                "matched_features": traits_dict
            })
            breed_utility_list.append({
                "breed_name": b_name,
                "breed_utility": utility_dict
            })

    except Exception as e:
        print("Supabase Query Error:", e)

    return matched_features_list, breed_utility_list