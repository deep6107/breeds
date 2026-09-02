from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from pydantic import BaseModel
from typing import Dict, Any

from breed_data.detect_breed import process_breed_detection
from process import create_result_file


app = FastAPI(
    title="Breed Recognition API",
    description="API for Indian cattle and buffalo breed recognition",
    version="1.0"
)


# ---------------------------------------------------------
# CORS
# ---------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


# ---------------------------------------------------------
# Request Model
# ---------------------------------------------------------

class BreedInput(BaseModel):
    features: Dict[str, Any]


# ---------------------------------------------------------
# Home Endpoint
# ---------------------------------------------------------

@app.get("/")
def home():
    return {
        "message": "Breed Recognition Backend is running"
    }


# ---------------------------------------------------------
# Breed Recognition Endpoint
# ---------------------------------------------------------

@app.post("/predict")
def predict_breed(data: BreedInput):

    # Get user-selected features
    incoming_payload = data.features

    # Send features to database/breed matching system
    matched_features_list, breed_utility_list = process_breed_detection(
        incoming_payload
    )

    # Count total features provided by user
    total_features = len(incoming_payload)

    # Create result file
    file_path = create_result_file(
        matched_features_list,
        breed_utility_list,
        total_features
    )

    # No matching breed
    if not matched_features_list:
        return {
            "success": False,
            "message": "No matching breed found.",
            "result_file": file_path
        }

    # Find best breed
    best_breed = max(
        matched_features_list,
        key=lambda x: x.get("total_matches", 0)
    )

    breed_name = best_breed.get("breed_name")
    matched_count = best_breed.get("total_matches", 0)

    # Calculate matching percentage
    percentage = (
        (matched_count / total_features) * 100
        if total_features > 0
        else 0
    )

    # Find breed information
    breed_information = next(
        (
            item.get("breed_utility", {})
            for item in breed_utility_list
            if item.get("breed_name") == breed_name
        ),
        {}
    )

    return {
        "success": True,
        "breed_name": breed_name,
        "matching_features": matched_count,
        "total_features": total_features,
        "matching_percentage": round(percentage, 2),
        "breed_information": breed_information,
        "result_file": file_path
    }


# ---------------------------------------------------------
# Result File Endpoint
# ---------------------------------------------------------

@app.get("/result")
def get_result():

    return FileResponse(
        "breed_result.txt",
        media_type="text/plain",
        filename="breed_result.txt"
    )