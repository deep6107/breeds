import uvicorn
from start_point import app

print("BREEDS AI PROJECT INITIALIZED\n")

if __name__ == "__main__":
    uvicorn.run("start_point:app", host="127.0.0.1", port=8000, reload=True)