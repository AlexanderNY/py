from fastapi import FastAPI, Path
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi.responses import FileResponse


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # * или конкретный URL фронтенда
    allow_methods=["POST", "GET"],
)
@app.get("/")
async def home():
    html_content = "<h2>Hello!</h2>"
    return HTMLResponse(content=html_content)

@app.get("/items/{item_id}")
def read_item(item_id: int = Path(ge=18, lt=111, default=None), q: str = Path(min_length=3, max_length=20,default=None)):
    data = {"item_id": item_id, "q": q}
    json_data = jsonable_encoder(data)
    return JSONResponse(content=json_data)



@app.post("/items/{item_id}")
async def create_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}

@app.get("/file")
def root():
    return FileResponse("index.html")