import os
import re
from fastapi import APIRouter, Request, UploadFile, File, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from breed_data.detect_breed import process_breed_detection
from breed_data.vision_extractor import extract_traits_from_image

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
        preview_path = "static/uploaded_preview.jpg"
        if os.path.exists(preview_path):
            os.remove(preview_path)

        input_data = {}

        # Handle Image Upload via Vision AI Model with Dynamic Mime Type Support
        if file is not None and file.filename != "":
            image_bytes = await file.read()
            if len(image_bytes) == 0:
                write_error_txt("Image is not clear re-upload after few min")
                return RedirectResponse(url="/result", status_code=303)
                
            os.makedirs("static", exist_ok=True)
            with open(preview_path, "wb") as img_out:
                img_out.write(image_bytes)
            
            # Pass file.content_type to correctly handle PNG, JPEG, and WebP formats
            input_data = extract_traits_from_image(image_bytes, mime_type=file.content_type)
            if not input_data:
                write_error_txt("Image is not clear re-upload after few min")
                return RedirectResponse(url="/result", status_code=303)

        # Handle Manual Trait Selection Dropdowns
        elif colour or hump or forehead or horns or ears or size:
            input_data = {
                "colour": colour,
                "hump": hump,
                "forehead": forehead,
                "horns": horns,
                "ears": ears,
                "size": size
            }
            input_data = {k: v for k, v in input_data.items() if v}
        else:
            write_error_txt("Image is not clear re-upload after few min")
            return RedirectResponse(url="/result", status_code=303)

        # Process matching features against Supabase database
        matched_features_list, breed_utility_list = process_breed_detection(input_data)

        if not matched_features_list:
            write_error_txt("Image is not clear re-upload after few min")
            return RedirectResponse(url="/result", status_code=303)

        # Write out results to breed.txt for HTML rendering
        with open("breed.txt", "w", encoding="utf-8") as f:
            top_match = matched_features_list[0]
            f.write(f"Breed : {top_match.get('breed_name')} : 95%\n")
            
            for idx, match in enumerate(matched_features_list, 1):
                b_name = match.get("breed_name", "Unknown")
                f.write(f"{idx}. {b_name}\n")
                
                utility_dict = {}
                for util in breed_utility_list:
                    if util.get("breed_name") == b_name:
                        utility_dict = util.get("breed_utility", {})
                        break
                
                for k, v in match.get("matched_features", {}).items():
                    f.write(f"{k.replace('_', ' ').title()} : {v}\n")
                
                for k, v in utility_dict.items():
                    f.write(f"{k.replace('_', ' ').title()} : {v}\n")
                
                f.write("\n")

        return RedirectResponse(url="/result", status_code=303)

    except Exception as e:
        print("--- PROCESSING ERROR ---")
        import traceback
        traceback.print_exc()
        write_error_txt("Image is not clear re-upload after few min")
        return RedirectResponse(url="/result", status_code=303)

def write_error_txt(message):
    with open("breed.txt", "w", encoding="utf-8") as f:
        f.write(f"Breed : {message} : 0%\n")
        f.write(f"1. {message}\n")
        f.write("Species : Unknown\n")
        f.write("Status : Failed\n")

def parse_breed_txt(filepath="breed.txt"):
    error_message = "Image is not clear re-upload after few min"
    error_response = {
        "title_breeds": error_message,
        "confidence": "0%",
        "breeds": [{
            "name": "Error",
            "details": {"species": "Unknown", "status": "Failed"}
        }]
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
            "confidence": "95%",
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

    except Exception as e:
        print("--- PARSE ERROR ---", e)
        return error_response

@router.get("/result", response_class=HTMLResponse)
async def serve_result_page(request: Request):
    parsed_data = parse_breed_txt("breed.txt")
    has_image = os.path.exists("static/uploaded_preview.jpg")
    return templates.TemplateResponse(request=request, name="result.html", context={"data": parsed_data, "has_image": has_image})