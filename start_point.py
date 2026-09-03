import os
import json
import subprocess
import sys
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

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
    # Route A: Image Upload
    if file and file.filename:
        temp_path = f"temp_{file.filename}"
        with open(temp_path, "wb") as buffer:
            buffer.write(await file.read())
            
        try:
            # Trigger llm/main.py as an external script
            result = subprocess.run(
                [sys.executable, "llm/main.py", temp_path],
                capture_output=True,
                text=True,
                check=True
            )
            
            # Grab the JSON string printed by your main.py file and convert it
            extracted_features = json.loads(result.stdout)
            
            # Save it so result.html can read it
            with open("final_result.json", "w") as f:
                json.dump(extracted_features, f, indent=4)
                
        except subprocess.CalledProcessError as e:
            # If main.py crashes, this catches the exact error message
            print(f"AI Script Error: {e.stderr}") 
            raise HTTPException(status_code=500, detail="Image processing failed.")
        except json.JSONDecodeError:
            print(f"Failed to parse JSON. Script output: {result.stdout}")
            raise HTTPException(status_code=500, detail="Invalid data returned from AI.")
        finally:
            # Clean up the uploaded image
            if os.path.exists(temp_path):
                os.remove(temp_path)

    # Route B: Manual Form Selections
    elif any([colour, hump, forehead, horns, ears, size]):
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

    return RedirectResponse(url="/result", status_code=303)

@app.get("/result", response_class=HTMLResponse)
async def serve_result_page(request: Request):
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

    return templates.TemplateResponse("result.html", {"request": request, "data": data})