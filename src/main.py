from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import weave
from src.routers import upload_router

origins = ["*"]
weave.init('jurassic-park')

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload_router)

@weave.op()
@app.get("/test")
async def test_route():
    return {"message": "This is a test route"}