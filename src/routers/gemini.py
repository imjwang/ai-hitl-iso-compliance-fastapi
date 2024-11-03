from fastapi import APIRouter
from pydantic import BaseModel
import vertexai
import os
from vertexai.generative_models import GenerativeModel, Part, GenerationConfig
import json

router = APIRouter()

iso_file_uri = "https://storage.googleapis.com/ait_nov_hackathon/ISO-29119-The-New-International-Software-Testing-Standards.pdf"
company_doc_uri = "https://storage.googleapis.com/ait_nov_hackathon/tinker/react.md"
reg = '<regulation>'
reg_close = '</regulation>'
company_doc = '<document>'
company_doc_close = '</document>'
REGULATORY_COMPLIANCE_PROMPT = f"""\
Please assess whether the document addresses and is compliant with the provided regulation.
Depending on the assessment, write "Compliant", "Partially Compliant" between <compliance></compliance> XML tags.

If the assessment is "partially compliant" provide a list of the document sections that need to be improved between <doc_sections></doc_sections> XML tags

Create a summary of the assessment that includes a specific, concise justification of the asessment. The summary should highlight which document sections are most relevant to the regulation and why. Provide the summary between <summary_compliance></summary_compliance> XML tags.\
"""

class RegulatoryComplianceOutput(BaseModel):
    compliance: str
    reason: str
    summary: str

def format_outputs(outputs: str) -> RegulatoryComplianceOutput:
    return RegulatoryComplianceOutput(
            compliance=outputs.split('<compliance>')[-1].split('</compliance>')[0],
            reason=outputs.split('<reason>')[-1].split('</reason>')[0],
            summary=outputs.split('<summary_compliance>')[-1].split('</summary_compliance>')[0]
        )

class GenerateRequest(BaseModel):
    iso_uri: str
    company_doc_uri: str


@router.post("/generate")
def generate_response(item: GenerateRequest) -> RegulatoryComplianceOutput:
    model = GenerativeModel(
    "gemini-1.5-flash",
    system_instruction='''You will be supplied with a document that forms part of an operational management framework.
You will be given a relevant governmental regulation that the document needs to address and be compliant with

You ALWAYS follow these guidelines when writing your response:
<guidelines>
- Carefully read through the supplied document.
- Carefully read through the supplied regulations.
- Identify sections within the regulations that are relevant to the document.
- Examine the document to identify any areas where the document is not compliant with the requirements.
- Only use information supplied in the prompt.
- For each of your selections, you provide reasoning to justify your selections.
</guidelines>
'''
    )

    iso_file_uri = f"gs://ait_nov_hackathon/{item.iso_uri}"
    company_doc_uri = f"gs://ait_nov_hackathon/tinker/{item.company_doc_uri}"
    print(iso_file_uri)
    print(company_doc_uri)

    # iso_file_uri = "https://storage.googleapis.com/ait_nov_hackathon/FileType.ISO/test.pdf"
    # company_doc_uri = "https://storage.googleapis.com/ait_nov_hackathon/tinker/deployment.md"

    iso_file = Part.from_uri(iso_file_uri, mime_type="application/pdf")
    company_file = Part.from_uri(company_doc_uri, mime_type="text/md")

    contents = [reg, iso_file, reg_close, company_doc, company_file, company_doc_close, REGULATORY_COMPLIANCE_PROMPT]

    response = model.generate_content(contents)
    return format_outputs(response.text)