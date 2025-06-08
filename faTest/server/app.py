from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # или конкретный URL фронтенда
    allow_methods=["POST", "GET"],
)
@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI server!"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}

@app.post("/items/{item_id}")
async def create_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}