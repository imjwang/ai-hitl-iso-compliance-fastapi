from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import weave
from src.routers import upload_router, gemini_router
import uvicorn
import os
from dotenv import load_dotenv
from google.oauth2 import service_account
import vertexai

# Load environment variables
load_dotenv()

# Allowed origins for CORS
origins = ["*"]

# Initialize FastAPI app
app = FastAPI()

# Google Cloud Service Account Info
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

# Verify that all required environment variables are set
print("Verifying Google Cloud service account environment variables...")
for key, value in service_account_info.items():
    print(f"{key}: {'Value set' if value else 'Not set'}")

if not all(service_account_info.values()):
    raise EnvironmentError("Required Google Cloud service account environment variables are not set.")

# Create credentials from the service account JSON
try:
    credentials = service_account.Credentials.from_service_account_info(service_account_info)
except Exception as e:
    raise EnvironmentError(f"Error creating Google Cloud credentials: {str(e)}")

# Initialize Vertex AI with credentials
vertexai.init(
    project=os.getenv("GCP_PROJECT_ID"),
    location=os.getenv("GOOGLE_CLOUD_REGION"),
    credentials=credentials
)

# Initialize Weave
weave.init('jurassic-park')

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(upload_router)
app.include_router(gemini_router)

# Test route
@weave.op()
@app.get("/test")
async def test_route():
    return {"message": "This is a test route"}

# Run the app with Uvicorn if executed as the main module
if __name__ == "__main__":
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
