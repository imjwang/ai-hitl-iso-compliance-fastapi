from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import weave
from src.routers import upload_router, gemini_router
import uvicorn
import json
from google.oauth2 import service_account
from google.cloud import aiplatform
import os
from dotenv import load_dotenv
import vertexai


load_dotenv()

origins = ["*"]

app = FastAPI()
service_account_info = {
    "type": os.getenv("GCP_TYPE"),
    "project_id": os.getenv("GCP_PROJECT_ID"), 
    "private_key_id": os.getenv("GCP_PRIVATE_KEY_ID"),
    "private_key": os.getenv("GCP_PRIVATE_KEY"),
    "client_email": os.getenv("GCP_CLIENT_EMAIL"),
    "client_id": os.getenv("GCP_CLIENT_ID"),
    "auth_uri": os.getenv("GCP_AUTH_URI"),
    "token_uri": os.getenv("GCP_TOKEN_URI"),
    "auth_provider_x509_cert_url": os.getenv("GCP_AUTH_PROVIDER_X509_CERT_URL"),
    "client_x509_cert_url": os.getenv("GCP_CLIENT_X509_CERT_URL"),
    "universe_domain": os.getenv("GCP_UNIVERSE_DOMAIN"),
}
print(service_account_info)
# Create credentials from the service account JSON
credentials = service_account.Credentials.from_service_account_info(service_account_info)

vertexai.init(
    project=os.getenv("GCP_PROJECT_ID"),
    location=os.getenv("GOOGLE_CLOUD_REGION"),
    credentials=credentials
)
weave.init('jurassic-park')

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload_router)
app.include_router(gemini_router)


@weave.op()
@app.get("/test")
async def test_route():
    return {"message": "This is a test route"}

if __name__ == "__main__":
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
