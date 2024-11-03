from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from restack_ai import Restack
import uvicorn
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

def run_app():
    uvicorn.run("src.app:app", host="0.0.0.0", port=8000, reload=True)

if __name__ == '__main__':
    run_app()