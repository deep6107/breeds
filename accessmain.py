from fastapi import FastAPI
from contextlib import asynccontextmanager
from start_point import router as start_point_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("BREEDS AI PROJECT INITIALIZED")
    print("\n")
    yield 
app = FastAPI(lifespan=lifespan)

app.include_router(start_point_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("accessmain:app", host="127.0.0.1", port=8000, reload=True)