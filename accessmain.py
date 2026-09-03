import uvicorn
from start_point import app

print("BREEDS AI PROJECT INITIALIZED\n")

if __name__ == "__main__":
    uvicorn.run("start_point:app", host="0.0.0.0", port=8000, reload=True)