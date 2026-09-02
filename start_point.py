import json
from contextlib import asynccontextmanager
from fastapi import FastAPI, APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import HTMLResponse
from test_llm import get_ai_features, fetch_breed_data
router = APIRouter()
@router.get("/")
async def load_frontend():
    try:
        with open("index.html", "r") as file:
            return HTMLResponse(content=file.read())
    except FileNotFoundError:
        return HTMLResponse(content="<h2>Error: index.html not found in folder!</h2>", status_code=404)

async def get_features(file: UploadFile = File(None), manual_features: str = Form(None)) -> dict:
    if file and file.filename:
        print(f">>> Frontend sent image: {file.filename}. Routing to LLM...")
        contents = await file.read()
        return get_ai_features(contents)
    elif manual_features:
        print(">>> Frontend sent manual JSON. Bypassing LLM...")
        return json.loads(manual_features)
    raise HTTPException(status_code=400, detail="Must provide 'file' or 'manual_features'.")
@router.post("/receive-input")
async def receive_input(
    file: UploadFile = File(None),
    manual_features: str = Form(None)
):
    try:
        extracted_features = await get_features(file, manual_features)
        if not extracted_features:
            raise HTTPException(status_code=404, detail="Extraction failed.")
        list_1, list_2 = fetch_breed_data(extracted_features)

        return {
            "status": "success",
            "list_1_matched_features": list_1,
            "list_2_breed_utility": list_2
        }
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON format.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
