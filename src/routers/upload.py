from fastapi import FastAPI, UploadFile, File, Form, HTTPException, APIRouter
from google.cloud import storage
import os
from enum import Enum
from typing import List
from dotenv import load_dotenv
load_dotenv()

# Initialize FastAPI application
app = FastAPI()

# Initialize APIRouter for upload functionality
router = APIRouter()

# Enum for File Types
class FileType(str, Enum):
    ISO = "ISO"
    CORPUS = "Corpus"

# Google Cloud Storage configuration
GCP_BUCKET_NAME = os.getenv("GCP_BUCKET_NAME")
GCP_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

if not GCP_BUCKET_NAME or not GCP_CREDENTIALS:
    raise EnvironmentError("Environment variables for GCP_BUCKET_NAME and GOOGLE_APPLICATION_CREDENTIALS must be set.")

storage_client = storage.Client()

async def upload_to_gcp(file: UploadFile, file_type: FileType) -> str:
    try:
        bucket = storage_client.bucket(GCP_BUCKET_NAME)
        blob = bucket.blob(f"{file_type}/{file.filename}")
        blob.upload_from_file(file.file, content_type=file.content_type)
        return f"File {file.filename} uploaded to GCP successfully."
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload file: {str(e)}")

@router.post("/upload_files/")
async def upload_files(
    file_type: FileType = Form(...),
    files: List[UploadFile] = File(...)
):
    uploaded_files = []
    for file in files:
        result = await upload_to_gcp(file, file_type)
        uploaded_files.append(result)

    return {"detail": uploaded_files}

@router.get("/list_files/")
async def list_files():
    try:
        bucket = storage_client.bucket(GCP_BUCKET_NAME)
        blobs = bucket.list_blobs()
        file_urls = [f"https://storage.googleapis.com/{GCP_BUCKET_NAME}/{blob.name}" for blob in blobs]
        return {"files": file_urls}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list files: {str(e)}")

# Include the router in the FastAPI app
app.include_router(router)
