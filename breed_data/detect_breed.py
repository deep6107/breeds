import os
import json
from dotenv import load_dotenv
from supabase import create_client
from .info_breed import get_breed_utility_details

load_dotenv()
supabase = create_client(os.environ.get("SUPABASE_URL"), os.environ.get("SUPABASE_KEY"))

def find_best_matching_breeds_features_only(input_data):
    try:
        # Pathway 1: Direct breed name lookup (triggered by image upload / vision extractor)
        breed_name_query = input_data.get("breed_name", "").strip().lower()
        if breed_name_query:
            response = supabase.table("breed_features").select("*").ilike("breed_name", f"%{breed_name_query}%").execute()
            rows = response.data
            
            if rows:
                matches = []
                for row in rows:
                    matches.append({
                        "breed_id": row.get("breed_id"),
                        "breed_name": row.get("breed_name"),
                        "total_matches": 10,
                        "matched_features": {k: v for k, v in row.items() if k not in ["breed_id", "breed_name"]}
                    })
                return {"highest_score": 10, "total_results": len(matches), "matches": matches}

        # Pathway 2: Original feature-matching logic (triggered by manual dropdown form inputs)
        all_breeds = supabase.table("breed_features").select("*").execute().data
        if not all_breeds:
            return {"highest_score": 0, "total_results": 0, "matches": []}
        
        normalized_input = {str(k).lower(): str(v).strip().lower() for k, v in input_data.items() if v}
        
        surviving_breeds = []
        max_matches = 0
        
        for row in all_breeds:
            current_match_count = 0
            current_matched_traits = {}
            
            for db_column, db_value in row.items():
                col_lower = db_column.lower()
                if col_lower in ["breed_id", "breed_name", "species"]:
                    continue
                    
                if col_lower in normalized_input and db_value is not None:
                    clean_db_value = str(db_value).strip().lower()
                    user_value = normalized_input[col_lower]
                    
                    user_words = set(user_value.split())
                    db_words = set(clean_db_value.split())
                    
                    if user_value in clean_db_value or clean_db_value in user_value or user_words.intersection(db_words):
                        current_match_count += 1
                        current_matched_traits[db_column] = db_value
                        
            if current_match_count == 0 and "species" in normalized_input:
                db_species = str(row.get("species", "")).lower()
                if normalized_input["species"] in db_species or db_species in normalized_input["species"]:
                    current_match_count = 1

            surviving_breeds.append({
                "breed_id": row.get("breed_id"),
                "breed_name": row.get("breed_name"),
                "total_matches": current_match_count,
                "matched_features": current_matched_traits
            })
            
            if current_match_count > max_matches:
                max_matches = current_match_count
                
        if max_matches == 0 and all_breeds:
            b = all_breeds[0]
            final_winners = [{
                "breed_id": b.get("breed_id"),
                "breed_name": b.get("breed_name"),
                "total_matches": 1,
                "matched_features": {k: v for k, v in b.items() if k not in ["breed_id", "breed_name"]}
            }]
            max_matches = 1
        else:
            final_winners = [b for b in surviving_breeds if b["total_matches"] == max_matches and max_matches > 0]

        return {
            "highest_score": max_matches,
            "total_results": len(final_winners),
            "matches": final_winners
        }

    except Exception as e:
        print("Supabase Processing Error:", e)
        return {"highest_score": 0, "total_results": 0, "matches": []}

def process_breed_detection(incoming_payload):
    feature_data = find_best_matching_breeds_features_only(incoming_payload)
    internal_matches = feature_data.get("matches", [])
    
    matched_features_list = []
    for m in internal_matches:
        matched_features_list.append({
            "breed_name": m.get("breed_name"),
            "total_matches": m.get("total_matches"),
            "matched_features": m.get("matched_features")
        })
    
    utility_output_raw = get_breed_utility_details(feature_data)
    utility_data = json.loads(utility_output_raw) if isinstance(utility_output_raw, str) else utility_output_raw
    breed_utility_list = utility_data.get("matches", [])
    
    return matched_features_list, breed_utility_list