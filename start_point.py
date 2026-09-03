import os
import json
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Mount static files and set up Jinja2 templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def serve_home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/get-features")
async def get_features(
    file: UploadFile = File(None),
    colour: str = Form(None),
    hump: str = Form(None),
    forehead: str = Form(None),
    horns: str = Form(None),
    ears: str = Form(None),
    size: str = Form(None)
):
    try:
        from llm.main import process_cattle_image
        if file and file.filename:
            temp_path = f"temp_{file.filename}"
            with open(temp_path, "wb") as buffer:
                buffer.write(await file.read())
            try:
                extracted_features = process_cattle_image(temp_path)
                with open("final_result.json", "w") as f:
                    json.dump(extracted_features, f, indent=4)
            finally:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
    except ImportError:
        pass

    if any([colour, hump, forehead, horns, ears, size]):
        manual_result = {
            "predicted_breed": "Manual Detection",
            "confidence": "N/A",
            "origin": "Unknown",
            "species": "Cattle/Buffalo",
            "type": "Selected",
            "milk_fat": "Unknown",
            "known_for": "Manual Inputs",
            "benefits": f"Traits: {colour}, {horns}"
        }
        with open("final_result.json", "w") as f:
            json.dump(manual_result, f, indent=4)

    # Redirect the browser to the /result page URL
    return RedirectResponse(url="/result", status_code=303)

@app.get("/result", response_class=HTMLResponse)
async def serve_result_page(request: Request):
    # Default fallback data if the JSON is missing or incomplete
    data = {
        "predicted_breed": "Analysis Pending",
        "confidence": "0%",
        "origin": "N/A",
        "species": "N/A",
        "type": "N/A",
        "milk_fat": "N/A",
        "known_for": "N/A",
        "benefits": "N/A"
    }

    if os.path.exists("final_result.json"):
        try:
            with open("final_result.json", "r") as f:
                loaded_data = json.load(f)
                if isinstance(loaded_data, dict):
                    data.update(loaded_data)
        except Exception:
            pass

    # This passes the Python 'data' dictionary directly into the HTML file
    return templates.TemplateResponse("result.html", {"request": request, "data": data})