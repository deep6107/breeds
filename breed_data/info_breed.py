# info_breed.py

import os
import json
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()
supabase = create_client(os.environ.get("SUPABASE_URL"), os.environ.get("SUPABASE_KEY"))

def get_breed_utility_details(feature_matching_output):
    if isinstance(feature_matching_output, str):
        data = json.loads(feature_matching_output)
    else:
        data = feature_matching_output
        
    matched_breeds = data.get("matches", []) if isinstance(data, dict) else data
    breed_utility_list = []
    
    for breed in matched_breeds:
        b_id = breed.get("breed_id")
        
        if b_id is not None:
            utility_response = supabase.table("breed_utility").select("*").eq("breed_id", b_id).execute()
            utility_data = utility_response.data[0] if utility_response.data else {}
            
            # Remove any occurrence of breed_id or redundant breed_name from utility data
            utility_data.pop("breed_id", None)
            utility_data.pop("breed_name", None)
            
            breed_utility_list.append({
                "breed_name": breed.get("breed_name"),
                "breed_utility": utility_data
            })
        
    final_payload = {
        "total_results": len(breed_utility_list),
        "matches": breed_utility_list
    }
    
    return json.dumps(final_payload, indent=2)