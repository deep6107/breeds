import os
import json
from dotenv import load_dotenv
from supabase import create_client
from .info_breed import get_breed_utility_details

load_dotenv()
supabase = create_client(os.environ.get("SUPABASE_URL"), os.environ.get("SUPABASE_KEY"))

def find_best_matching_breeds_features_only(input_data):
    all_breeds = supabase.table("breed_features").select("*").execute().data
    
    normalized_input = {str(k).lower(): str(v).strip().lower() for k, v in input_data.items()}
    
    surviving_breeds = []
    max_matches = 0
    
    for row in all_breeds:
        mandatory_keys = ["colour", "hump", "ears"]
        failed_mandatory = False
        
        for key in mandatory_keys:
            if key in normalized_input:
                user_val = normalized_input[key]
                db_val = str(row.get(key, "")).strip().lower()
                
                if not (user_val in db_val or db_val in user_val):
                    failed_mandatory = True
                    break
        
        if failed_mandatory:
            continue 
            
        current_match_count = 0
        current_matched_traits = {}
        
        for db_column, db_value in row.items():
            col_lower = db_column.lower()
            if col_lower in ["breed_id", "breed_name", "species"]:
                continue
                
            if col_lower in normalized_input and db_value is not None:
                clean_db_value = str(db_value).strip().lower()
                user_value = normalized_input[col_lower]
                
                if user_value in clean_db_value or clean_db_value in user_value:
                    current_match_count += 1
                    current_matched_traits[db_column] = db_value
                    
        surviving_breeds.append({
            "breed_id": row.get("breed_id"),
            "breed_name": row.get("breed_name"),
            "total_matches": current_match_count,
            "matched_features": current_matched_traits
        })
        
        if current_match_count > max_matches:
            max_matches = current_match_count
            
    final_winners = [b for b in surviving_breeds if b["total_matches"] == max_matches and max_matches > 0]

    final_payload = {
        "highest_score": max_matches,
        "total_results": len(final_winners),
        "matches": final_winners
    }
    
    return final_payload

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