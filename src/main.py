from fastapi import FastAPI, Form, HTTPException, UploadFile
from google.cloud import storage
from src.routers.upload import upload_to_gcp, FileType
import os
import re
import io
from fastapi.datastructures import UploadFile as FastAPIUploadFile

app = FastAPI()

# Google Cloud Storage configuration
GCP_BUCKET_NAME = os.getenv("GCP_BUCKET_NAME")
GCP_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

if not GCP_BUCKET_NAME or not GCP_CREDENTIALS:
    raise EnvironmentError("Environment variables for GCP_BUCKET_NAME and GOOGLE_APPLICATION_CREDENTIALS must be set.")

storage_client = storage.Client()

@app.post("/fix_compliance_file/")
async def fix_compliance_file(
    compliance: str = Form(...),
    doc_sections: str = Form(...),
    summary_compliance: str = Form(...),
    file_url_gcp: str = Form(...),
):
    try:
        # Clean up the file URL if it starts with 'gs://'
        if file_url_gcp.startswith("gs://"):
            file_url_gcp = file_url_gcp.replace(f"gs://{GCP_BUCKET_NAME}/", "")
        else:
            file_url_gcp = file_url_gcp.replace(f"https://storage.googleapis.com/{GCP_BUCKET_NAME}/", "")

        # Download the file from GCP
        bucket = storage_client.bucket(GCP_BUCKET_NAME)
        blob = bucket.blob(file_url_gcp)

        if not blob.exists():
            raise HTTPException(status_code=404, detail="The specified file does not exist in the bucket.")

        original_file_content = blob.download_as_text()

        # Generate prompt for LLM to fix the document
        prompt = f"""
        You are an expert Compliance Auditor. Your task is to generate a revised document based on the following information:
        
        Compliance Status: {compliance}
        Document Sections to be Improved: {doc_sections}
        Summary of Compliance Assessment: {summary_compliance}
        
        Original Document Content:
        {original_file_content}
        
        Please create a new version of the document that addresses the compliance issues identified above.
        """

        # Placeholder for LLM call - Replace this with the actual LLM integration
        fixed_content = "<fixed_document>Revised content based on the provided analysis.</fixed_document>"

        # Determine the new version number
        version_match = re.search(r'v(\d+)$', file_url_gcp)
        if version_match:
            current_version = int(version_match.group(1))
            new_version = current_version + 1
        else:
            new_version = 1

        new_blob_name = re.sub(r'v(\d+)$', f'v{new_version}', file_url_gcp) if version_match else f"{file_url_gcp}_v{new_version}"

        # Upload the new fixed document to GCP using existing upload function
        fixed_file = FastAPIUploadFile(filename=f"{new_blob_name}.xml", file=io.BytesIO(fixed_content.encode("utf-8")))
        fixed_file_url = await upload_to_gcp(fixed_file, FileType.CORPUS)

        return {"message": "New fixed file created successfully.", "fixed_file_url": fixed_file_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fix file: {str(e)}")

# Run this command to start FastAPI (example)
# uvicorn filename:app --reload
