from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from process import create_result_file

app = FastAPI()


# Allow frontend to communicate with backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.get("/")
def home():
    return {
        "message": "Breed Recognition Backend is running"
    }


@app.get("/result")
def get_result():

    # Temporary test data
    matched_features_list = [
        {
            "breed_name": "Surti",
            "total_matches": 5,
            "matched_features": {
                "colour": "black",
                "hump": "medium",
                "ears": "medium"
            }
        }
    ]

    breed_utility_list = [
        {
            "breed_name": "Surti",
            "breed_utility": {
                "origin": "Gujarat",
                "type": "Milch",
                "milk_fat": 7.5,
                "known_for": "Highest milk fat ratio in medium body",
                "benefits": "Requires very low daily feeding quantities",
                "species": "Buffalo"
            }
        }
    ]

    file_path = create_result_file(
        matched_features_list,
        breed_utility_list,
        6
    )

    return FileResponse(
        file_path,
        media_type="text/plain",
        filename="breed_result.txt"
    )