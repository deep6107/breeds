import os
import re
from fastapi import APIRouter, Request, UploadFile, File, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.post("/get-features")
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
        # Placeholder for your matching logic or database/CSV lookup
        # This writes a sample structured breed.txt file for testing
        with open("breed.txt", "w", encoding="utf-8") as f:
            f.write("Breed : Surti, Nagpuri : 83%\n")
            f.write("1. SURTI\n")
            f.write("Origin : Gujarat\n")
            f.write("Species : Buffalo\n")
            f.write("Type : Milch\n")
            f.write("Milk Fat : 7.5%\n")
            f.write("Known For : Highest milk fat ratio\n")
            f.write("Benefits : Low daily feeding requirement\n\n")
            f.write("2. NAGPURI\n")
            f.write("Origin : Maharashtra\n")
            f.write("Species : Buffalo\n")
            f.write("Type : Dual\n")
            f.write("Milk Fat : 6.8%\n")
            f.write("Known For : Endurance and draught capability\n")
            f.write("Benefits : Adaptable to dry climates\n")

        return RedirectResponse(url="/result", status_code=303)

    except Exception as e:
        print("--- PROCESSING ERROR ---")
        import traceback
        traceback.print_exc()
        return RedirectResponse(url="/result?error=true", status_code=303)


def parse_breed_txt(filepath="breed.txt"):
    error_response = {
        "title_breeds": "Can't fetch the breed try after few minutes",
        "confidence": "0%",
        "breeds": []
    }

    if not os.path.exists(filepath):
        return error_response

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        if not content.strip():
            return error_response

        data = {
            "title_breeds": "Detected Breeds",
            "confidence": "83%",
            "breeds": []
        }
        
        lines = [line.strip() for line in content.split("\n") if line.strip()]
        current_breed = None

        for line in lines:
            if line.lower().startswith("breed :") and not current_breed and len(data["breeds"]) == 0:
                parts = line.split(":")
                if len(parts) >= 2:
                    data["title_breeds"] = parts[1].strip()
                if len(parts) >= 3:
                    data["confidence"] = parts[2].strip()
                continue

            if re.match(r"^\d+\s*[\.\-]", line) or (line[0].isdigit() and "." in line and ":" not in line):
                if current_breed and current_breed["details"]:
                    data["breeds"].append(current_breed)
                
                breed_name = re.sub(r"^\d+\s*[\.\-]\s*", "", line).replace(":", "").strip()
                current_breed = {"name": breed_name, "details": {}}
                continue

            if ":" in line:
                parts = line.split(":", 1)
                key = parts[0].strip().lower().replace(" ", "_")
                val = parts[1].strip()
                
                if "confidence" in key:
                    data["confidence"] = val
                elif current_breed is not None:
                    current_breed["details"][key] = val

        if current_breed and current_breed["details"]:
            data["breeds"].append(current_breed)

        if not data["breeds"]:
            return error_response

        return data

    except Exception:
        return error_response


@router.get("/result", response_class=HTMLResponse)
async def serve_result_page(request: Request):
    parsed_data = parse_breed_txt("breed.txt")
    return templates.TemplateResponse(request=request, name="result.html", context={"data": parsed_data})