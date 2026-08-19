from fastapi import (
    FastAPI,
    UploadFile,
    File,
    Form,
    HTTPException
)

from fastapi.responses import FileResponse

from PIL import Image

import io
import os
import uuid

from datetime import datetime
from zoneinfo import ZoneInfo

from utils.prediction import (
    predict_image,
    get_severity
)

from database import (
    create_database,
    save_report,
    get_all_reports,
    update_report_status
)

from report_gen import (
    generate_report_pdf
)


# ============================================================
# TIMEZONE
# ============================================================

INDIA_TIMEZONE = ZoneInfo(
    "Asia/Kolkata"
)


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="AI Road Infrastructure API",
    description="Backend API for AI-based road damage detection",
    version="1.0.0"
)


# ============================================================
# DATABASE
# ============================================================

create_database()


# ============================================================
# HOME
# ============================================================

@app.get("/")
def home():

    return {
        "message": "AI Road Infrastructure API is running"
    }


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
def health_check():

    return {
        "status": "healthy"
    }


# ============================================================
# CURRENT INDIA TIME
# ============================================================

def get_india_time():

    return datetime.now(
        INDIA_TIMEZONE
    )


# ============================================================
# PREDICT ROAD DAMAGE
# ============================================================

@app.post("/predict")
async def predict(
    file: UploadFile = File(...)
):

    try:

        image_bytes = await file.read()

        image = Image.open(
            io.BytesIO(image_bytes)
        ).convert("RGB")

        predicted_class, confidence, probabilities = predict_image(
            image
        )

        severity, priority = get_severity(
            predicted_class
        )

        return {

            "prediction":
                predicted_class,

            "confidence":
                round(
                    confidence,
                    2
                ),

            "severity":
                severity,

            "priority":
                priority,

            "probabilities": {

                name:
                    round(
                        value,
                        2
                    )

                for name, value
                in probabilities.items()
            }
        }

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )


# ============================================================
# CREATE ROAD REPORT
# ============================================================

@app.post("/reports")
async def create_report(

    file: UploadFile = File(...),

    location: str = Form(...),

    road_area: str = Form(...),

    description: str = Form("")
):

    try:

        # ----------------------------------------------------
        # READ IMAGE
        # ----------------------------------------------------

        image_bytes = await file.read()

        image = Image.open(
            io.BytesIO(image_bytes)
        ).convert("RGB")


        # ----------------------------------------------------
        # AI PREDICTION
        # ----------------------------------------------------

        predicted_class, confidence, _ = predict_image(
            image
        )

        severity, priority = get_severity(
            predicted_class
        )


        # ----------------------------------------------------
        # INDIA DATE AND TIME
        # ----------------------------------------------------

        current_time = get_india_time()

        reported_date = current_time.strftime(
            "%d-%m-%Y"
        )

        reported_time = current_time.strftime(
            "%I:%M:%S %p"
        )

        reported_datetime = current_time.strftime(
            "%d-%m-%Y %I:%M:%S %p IST"
        )


        # ----------------------------------------------------
        # REPORT ID
        # ----------------------------------------------------

        report_id = (
            "RI-"
            + current_time.strftime(
                "%Y%m%d"
            )
            + "-"
            + uuid.uuid4().hex[:6].upper()
        )


        # ----------------------------------------------------
        # REPORT DIRECTORY
        # ----------------------------------------------------

        report_directory = os.path.join(
            "reports",
            report_id
        )

        os.makedirs(
            report_directory,
            exist_ok=True
        )


        # ----------------------------------------------------
        # SAVE IMAGE
        # ----------------------------------------------------

        image_path = os.path.join(
            report_directory,
            "road_image.jpg"
        )

        image.save(
            image_path,
            format="JPEG",
            quality=90
        )


        # ----------------------------------------------------
        # GENERATE PDF
        # ----------------------------------------------------

        pdf_path = generate_report_pdf(

            report_id=report_id,

            issue=predicted_class,

            confidence=confidence,

            severity=severity,

            priority=priority,

            location=location,

            road_area=road_area,

            description=description,

            reported_date=reported_date,

            reported_time=reported_datetime,

            status="Reported",

            image_path=image_path
        )


        # ----------------------------------------------------
        # SAVE TO DATABASE
        # ----------------------------------------------------

        save_report(

            report_id=report_id,

            issue=predicted_class,

            confidence=confidence,

            severity=severity,

            priority=priority,

            location=location,

            road_area=road_area,

            description=description,

            reported_date=reported_date,

            reported_time=reported_datetime,

            status="Reported",

            image_path=image_path,

            pdf_path=pdf_path
        )


        # ----------------------------------------------------
        # RESPONSE
        # ----------------------------------------------------

        return {

            "message":
                "Road issue reported successfully",

            "report_id":
                report_id,

            "prediction":
                predicted_class,

            "confidence":
                round(
                    confidence,
                    2
                ),

            "severity":
                severity,

            "priority":
                priority,

            "location":
                location,

            "road_area":
                road_area,

            "description":
                description,

            "reported_date":
                reported_date,

            "reported_time":
                reported_datetime,

            "status":
                "Reported",

            "pdf_available":
                True
        }


    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )


# ============================================================
# GET ALL REPORTS
# ============================================================

@app.get("/reports")
def get_reports():

    try:

        reports = get_all_reports()

        return {
            "reports": reports
        }

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )


# ============================================================
# GET REPORT IMAGE
# ============================================================

@app.get("/reports/{report_id}/image")
def get_report_image(
    report_id: str
):

    try:

        reports = get_all_reports()

        selected_report = None

        for report in reports:

            if report["report_id"] == report_id:

                selected_report = report

                break


        if selected_report is None:

            raise HTTPException(
                status_code=404,
                detail="Report not found"
            )


        image_path = selected_report.get(
            "image_path"
        )


        if not image_path:

            raise HTTPException(
                status_code=404,
                detail="Road image not available"
            )


        if not os.path.exists(
            image_path
        ):

            raise HTTPException(
                status_code=404,
                detail="Road image file not found"
            )


        return FileResponse(

            path=image_path,

            media_type="image/jpeg"
        )


    except HTTPException:

        raise


    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )


# ============================================================
# UPDATE REPORT STATUS
# ============================================================

@app.put("/reports/{report_id}/status")
def change_report_status(

    report_id: str,

    status: str
):

    allowed_statuses = [

        "Reported",

        "In Progress",

        "Resolved"
    ]


    if status not in allowed_statuses:

        raise HTTPException(

            status_code=400,

            detail=(
                "Invalid status. "
                "Use: Reported, "
                "In Progress, or Resolved."
            )
        )


    try:

        updated = update_report_status(

            report_id,

            status
        )


        if not updated:

            raise HTTPException(

                status_code=404,

                detail="Report not found"
            )


        return {

            "message":
                "Status updated successfully",

            "report_id":
                report_id,

            "status":
                status
        }


    except HTTPException:

        raise


    except Exception as error:

        raise HTTPException(

            status_code=500,

            detail=str(error)
        )


# ============================================================
# DOWNLOAD PDF REPORT
# ============================================================

@app.get("/reports/{report_id}/pdf")
def download_report_pdf(

    report_id: str
):

    try:

        reports = get_all_reports()

        selected_report = None

        for report in reports:

            if report["report_id"] == report_id:

                selected_report = report

                break


        if selected_report is None:

            raise HTTPException(

                status_code=404,

                detail="Report not found"
            )


        pdf_path = selected_report.get(
            "pdf_path"
        )


        if not pdf_path:

            raise HTTPException(

                status_code=404,

                detail="PDF report not available"
            )


        if not os.path.exists(
            pdf_path
        ):

            raise HTTPException(

                status_code=404,

                detail="PDF file not found"
            )


        return FileResponse(

            path=pdf_path,

            media_type="application/pdf",

            filename=(
                f"{report_id}_road_report.pdf"
            )
        )


    except HTTPException:

        raise


    except Exception as error:

        raise HTTPException(

            status_code=500,

            detail=str(error)
        )