import sys
import os

# Ensure project root directory is in sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import io
import cv2
import numpy as np
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional

from cv_engine.reagent_classifier import ReagentClassifier, REAGENT_DATABASE
from backend.chain_of_custody import ChainOfCustodyLedger
from backend.report_generator import PDFReportGenerator

app = FastAPI(
    title="Digital Companion for Field Drug Testing API",
    description="Backend services for SIH26231 Field Drug Testing with CV Color Calibration & SHA-256 Chain of Custody",
    version="1.0.0"
)

# Initialize Core Services
classifier = ReagentClassifier()
ledger = ChainOfCustodyLedger(ledger_file="backend/chain_ledger.json")


class CaseSubmissionRequest(BaseModel):
    case_id: str
    officer_id: str
    sample_id: str
    location: str
    reagent_used: str
    presumptive_category: str
    confidence_score: float
    detected_color_description: str
    delta_e_distance: float
    cross_reactivity_warnings: list[str]
    recommended_lab_confirmation: str
    signature: Optional[str] = "OFFICER_DIGITAL_SIGNATURE_SHA256"


@app.get("/")
def read_root():
    return {
        "status": "online",
        "service": "SIH26231 Field Drug Testing Digital Companion API",
        "version": "1.0.0"
    }


@app.get("/api/reagents")
def get_supported_reagents():
    """
    Returns list of supported colorimetric reagent kits and candidate target drugs.
    """
    return {
        "reagents": list(REAGENT_DATABASE.keys()),
        "details": REAGENT_DATABASE
    }


@app.post("/api/analyze-test")
async def analyze_reagent_test(
    reagent_name: str = Form(...),
    file: UploadFile = File(...)
):
    """
    Uploads a sample test spot image, extracts calibrated color values, and returns presumptive drug result.
    """
    try:
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if img is None:
            raise HTTPException(status_code=400, detail="Invalid image file uploaded.")

        # Run CV Engine classification
        analysis_result = classifier.analyze_patch(img, reagent_name=reagent_name)
        return JSONResponse(content=analysis_result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/cases/create")
def create_case_record(req: CaseSubmissionRequest):
    """
    Registers a new field case, sealing it into the SHA-256 tamper-evident chain of custody ledger.
    """
    block = ledger.add_case_record(
        case_id=req.case_id,
        officer_id=req.officer_id,
        sample_id=req.sample_id,
        location=req.location,
        reagent=req.reagent_used,
        presumptive_result=req.presumptive_category,
        confidence=req.confidence_score,
        signature=req.signature
    )

    # Attach detailed case data to return object
    case_full_data = {**req.dict(), **block}

    # Pre-generate PDF report
    pdf_path = f"reports/Report_{req.case_id}.pdf"
    PDFReportGenerator.generate_report(case_full_data, output_pdf_path=pdf_path)

    return {
        "message": "Case sealed into cryptographic chain of custody ledger.",
        "block": block,
        "pdf_report_path": pdf_path
    }


@app.get("/api/chain/verify")
def verify_ledger_chain():
    """
    Verifies cryptographic integrity of all field test records in the ledger.
    """
    is_valid, violations = ledger.verify_integrity()
    return {
        "is_chain_valid": is_valid,
        "total_records": len(ledger.get_all_blocks()),
        "violations": violations
    }


@app.get("/api/cases/{case_id}/pdf")
def download_case_pdf(case_id: str):
    """
    Downloads the official court-ready PDF Field Evidence Report for a given case ID.
    """
    pdf_path = f"reports/Report_{case_id}.pdf"
    if os.path.exists(pdf_path):
        return FileResponse(pdf_path, media_type="application/pdf", filename=f"Report_{case_id}.pdf")
    else:
        raise HTTPException(status_code=404, detail="PDF report not found for this Case ID.")
