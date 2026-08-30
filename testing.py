import sys
import os
import json

# Ensure Python can locate modules from the root directory
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from breed_data.detect_breed import process_breed_detection

incoming_payload = {
    "colour": "black",       
    "hump": "none",  
    "ears": "short-alert",   
    "forehead": "flat",
    "horns": "sickle",
    "size": "medium"
}

list1, list2 = process_breed_detection(incoming_payload)

print("--- LIST 1: MATCHED FEATURES ---")
print(json.dumps(list1, indent=2))

print("\n--- LIST 2: BREED UTILITY INFO ---")
print(json.dumps(list2, indent=2))