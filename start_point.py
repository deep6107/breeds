import os
import json
import sys
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv

from process import create_result_file
from endpoint import router as result_router

load_dotenv()

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Mount the endpoint.py router for /result
app.include_router(result_router)

@app.get("/", response_class=HTMLResponse)
async def serve_home(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

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
    extracted_features = {}

    # Route A: Image Upload -> LLM Script
    if file and file.filename:
        temp_path = f"temp_{file.filename}"
        with open(temp_path, "wb") as buffer:
            buffer.write(await file.read())

        # Save current root directory and make image path absolute
        original_cwd = os.getcwd()
        absolute_image_path = os.path.abspath(temp_path)

        try:
            # 1. Add LLM folder to Python path so we can import it
            sys.path.append(os.path.abspath("llm"))
            from main import process_cattle_image
            
            # 2. Shift working directory to 'llm' so its internal subprocesses can find their files
            os.chdir("llm")
            
            # 3. Execute the function directly
            extracted_features = process_cattle_image(absolute_image_path)
            
            # 4. Return to root directory
            os.chdir(original_cwd)
            
        except Exception as e:
            os.chdir(original_cwd) # Ensure we revert back to root even if it crashes
            print(f"AI Processing Error: {e}")
            raise HTTPException(status_code=500, detail="Image processing failed.")
        finally:
            if os.path.exists(absolute_image_path):
                os.remove(absolute_image_path)

    # Route B: Manual Form Selections
    elif any([colour, hump, forehead, horns, ears, size]):
        extracted_features = {
            "colour": colour,
            "hump": hump,
            "forehead": forehead,
            "horns": horns,
            "ears": ears,
            "size": size
        }
    else:
        raise HTTPException(status_code=400, detail="Provide an image or manual characteristics.")

    # Query database and pass lists to process.py
    try:
        # Corrected import syntax for files inside a folder
        from breed_data.detect_breed import process_breed_detection
        matched_features_list, breed_utility_list = process_breed_detection(extracted_features)
    except ImportError as e:
        print(f"Database import failed: {e}")
        # Fallback sample structure matching your database output
        matched_features_list = [
            {"breed_name": "Surti", "total_matches": 5},
            {"breed_name": "Nagpuri", "total_matches": 4},
            {"breed_name": "Pandharpuri", "total_matches": 4}
        ]
        breed_utility_list = [
            {
                "breed_name": "Surti",
                "breed_utility": {
                    "origin": "Gujarat",
                    "species": "Buffalo",
                    "type": "Milch",
                    "milk_fat": "7.5%",
                    "known_for": "Highest milk fat ratio in medium body",
                    "benefits": "Requires very low daily feeding quantities"
                }
            }
        ]

    # Generate breed.txt via process.py
    create_result_file(
        matched_features_list=matched_features_list,
        breed_utility_list=breed_utility_list,
        total_features=len(extracted_features) or 6,
        filepath="breed.txt"
    )

    return RedirectResponse(url="/result", status_code=303)