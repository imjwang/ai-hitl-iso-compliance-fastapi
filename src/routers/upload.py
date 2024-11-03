from fastapi import FastAPI, UploadFile, File, Form, HTTPException, APIRouter
from google.cloud import storage
import os
from enum import Enum
from typing import List
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import Annotated
load_dotenv()

# Initialize APIRouter for upload functionality
router = APIRouter()

# Enum for File Types
class FileType(str, Enum):
    ISO = "ISO"
    CORPUS = "Corpus"

# Google Cloud Storage configuration
GCP_BUCKET_NAME = os.getenv("GCP_BUCKET_NAME")
GCP_CREDENTIALS = {
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
    "universe_domain": os.getenv("GCP_UNIVERSE_DOMAIN")
}

if not GCP_BUCKET_NAME or not all(GCP_CREDENTIALS.values()):
    raise EnvironmentError("Required GCP environment variables are not set.")

storage_client = storage.Client.from_service_account_info(GCP_CREDENTIALS)

async def upload_to_gcp(file: UploadFile, file_type: FileType) -> str:
    try:
        bucket = storage_client.bucket(GCP_BUCKET_NAME)
        blob = bucket.blob(f"{file_type}/{file.filename}")
        blob.upload_from_file(file.file, content_type=file.content_type)
        return f"File {file.filename} uploaded to GCP successfully."
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload file: {str(e)}")

@router.post("/upload_files/")
async def upload_files(form: Annotated[str, Form()]):
    print(form)
    # files = [file for file in form.files.values()]
    # if not files:
    #     raise HTTPException(status_code=400, detail="No files provided")
    # uploaded_files = []
    # for file in files:
    #     # Need to seek to start of file before uploading since it may have been read
    #     file.file.seek(0)
    #     result = await upload_to_gcp(file, form.file_type)
    #     uploaded_files.append(result)

    return {"detail": "success"}

@router.get("/list_files/")
async def list_files():
    try:
        bucket = storage_client.bucket(GCP_BUCKET_NAME)
        blobs = bucket.list_blobs()
        file_urls = [f"https://storage.googleapis.com/{GCP_BUCKET_NAME}/{blob.name}" for blob in blobs]
        return {"files": file_urls}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list files: {str(e)}")
