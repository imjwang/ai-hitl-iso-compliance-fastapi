from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from restack_ai import Restack
import time
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
import weave
from src.client import client
# from src.routers import upload

origins = ["*"]
weave.init('jurassic-park')

app = FastAPI()

# app.include_router(upload.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@weave.op()
@app.get("/test")
async def test_route():
    return {"message": "This is a test route"}

# class InputParams(BaseModel):
#     user_content: str

# @weave.op()
# @app.post("/api/schedule")
# async def schedule_workflow(data: InputParams):
#     workflow_id = f"{int(time.time() * 1000)}-GeminiGenerateWorkflow"
#     runId = await client.schedule_workflow(
#         workflow_name="GeminiGenerateWorkflow",
#         workflow_id=workflow_id,
#         input=data
#     )

#     print(f"Scheduled workflow with ID: {workflow_id}")

#     result = await client.get_workflow_result(
#         workflow_id=workflow_id,
#         run_id=runId
#     )
#     return result

# class FeedbackParams(BaseModel):
#     feedback: str

# @weave.op()
# @app.post("/api/event/feedback")
# async def send_event_feedback(data: FeedbackParams):
#     await client.send_workflow_event(
#         workflow_name="GeminiGenerateWorkflow",
#         event_name="feedback",
#         input=data
#     )
#     return

# @weave.op()
# @app.post("/api/event/end")
# async def send_event_end():
#     await client.send_workflow_event(
#         workflow_name="GeminiGenerateWorkflow",
#         event_name="end"
#     )
#     return

def run_app():
    uvicorn.run("src.app:app", host="0.0.0.0", port=5000, reload=True)

if __name__ == '__main__':
    run_app()