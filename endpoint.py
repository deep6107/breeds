import os
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="templates")

def parse_breed_txt(filepath="breed.txt"):
    """Reads breed.txt and structures it for the dynamic HTML tabs."""
    data = {
        "title_breeds": "Analysis Pending",
        "confidence": "0%",
        "breeds": []
    }
    
    if not os.path.exists(filepath):
        return data

    with open(filepath, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f.readlines() if line.strip()]

    if not lines:
        return data

    # 1. Parse header line: "Breed : Surti, Nagpuri : 83%"
    first_line = lines[0]
    if first_line.startswith("Breed :"):
        parts = first_line.split(":")
        if len(parts) >= 3:
            data["title_breeds"] = parts[1].strip()
            data["confidence"] = parts[2].strip()

    # 2. Parse individual breed sections
    current_breed = None
    for line in lines[1:]:
        if line.startswith("-"):
            continue

        # Detect block header like "1.Surti:"
        if line[0].isdigit() and "." in line and line.endswith(":"):
            if current_breed:
                data["breeds"].append(current_breed)
            current_breed = {"name": line.replace(":", "").strip(), "details": {}}
        elif ":" in line and current_breed is not None:
            key, val = line.split(":", 1)
            current_breed["details"][key.strip()] = val.strip()

    if current_breed:
        data["breeds"].append(current_breed)

    return data

@router.get("/result", response_class=HTMLResponse)
async def serve_result_page(request: Request):
    parsed_data = parse_breed_txt("breed.txt")
    return templates.TemplateResponse("result.html", {"request": request, "data": parsed_data})