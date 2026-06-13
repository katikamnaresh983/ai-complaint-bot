import os
from pathlib import Path
import secrets
from types import SimpleNamespace
from urllib.parse import parse_qs
from xml.sax.saxutils import escape

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.responses import FileResponse, Response
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from . import ai, crud, database, models, schemas

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="AI Complaint Bot", version="0.1.0")
app.mount("/static", StaticFiles(directory="static"), name="static")
security = HTTPBasic()


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


def require_admin(credentials: HTTPBasicCredentials = Depends(security)):
    expected_username = os.getenv("ADMIN_USERNAME", "admin")
    expected_password = os.getenv("ADMIN_PASSWORD", "admin123")
    username_ok = secrets.compare_digest(credentials.username, expected_username)
    password_ok = secrets.compare_digest(credentials.password, expected_password)

    if not (username_ok and password_ok):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin login",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/", include_in_schema=False)
def dashboard_home(_admin: str = Depends(require_admin)):
    return FileResponse(Path("static/index.html"))


@app.get(
    "/dashboard/stats",
    response_model=schemas.DashboardStats,
    tags=["dashboard"],
)
def dashboard_stats(_admin: str = Depends(require_admin), db: Session = Depends(get_db)):
    return crud.get_dashboard_stats(db)


@app.post(
    "/bot/analyze",
    response_model=schemas.ComplaintAnalysis,
    tags=["bot"],
)
def analyze_complaint(complaint: schemas.ComplaintCreate, _admin: str = Depends(require_admin)):
    return ai.analyze_complaint(complaint.message, complaint.category)


@app.post(
    "/complaints/",
    response_model=schemas.ComplaintOut,
    status_code=status.HTTP_201_CREATED,
    tags=["complaints"],
)
def create_complaint(
    complaint: schemas.ComplaintCreate,
    _admin: str = Depends(require_admin),
    db: Session = Depends(get_db),
):
    return crud.create_complaint(db=db, complaint=complaint)


@app.get("/complaints/", response_model=list[schemas.ComplaintOut], tags=["complaints"])
def read_complaints(_admin: str = Depends(require_admin), db: Session = Depends(get_db)):
    return crud.get_complaints(db)


@app.get("/complaints/{complaint_id}", response_model=schemas.ComplaintOut, tags=["complaints"])
def read_complaint(
    complaint_id: int,
    _admin: str = Depends(require_admin),
    db: Session = Depends(get_db),
):
    complaint = crud.get_complaint(db, complaint_id)
    if complaint is None:
        raise HTTPException(status_code=404, detail="Complaint not found")
    return complaint


@app.patch("/complaints/{complaint_id}", response_model=schemas.ComplaintOut, tags=["complaints"])
def update_status(
    complaint_id: int,
    update: schemas.ComplaintUpdate,
    _admin: str = Depends(require_admin),
    db: Session = Depends(get_db),
):
    complaint = crud.update_complaint_status(db, complaint_id, update.status)
    if complaint is None:
        raise HTTPException(status_code=404, detail="Complaint not found")
    return complaint


@app.patch(
    "/complaints/{complaint_id}/category",
    response_model=schemas.ComplaintOut,
    tags=["complaints"],
)
def update_category(
    complaint_id: int,
    update: schemas.ComplaintCategoryUpdate,
    _admin: str = Depends(require_admin),
    db: Session = Depends(get_db),
):
    complaint = crud.update_complaint_category(db, complaint_id, update.category)
    if complaint is None:
        raise HTTPException(status_code=404, detail="Complaint not found")
    return complaint


@app.post(
    "/whatsapp/demo",
    response_model=schemas.WhatsAppReply,
    tags=["whatsapp"],
)
def whatsapp_demo(
    payload: schemas.WhatsAppMessage,
    _admin: str = Depends(require_admin),
    db: Session = Depends(get_db),
):
    complaint = _create_whatsapp_complaint(db, payload)
    return {
        "complaint_id": complaint.id,
        "reply": _build_whatsapp_reply(complaint),
        "complaint": complaint,
    }


@app.post("/whatsapp/webhook", tags=["whatsapp"])
async def whatsapp_webhook(request: Request, db: Session = Depends(get_db)):
    body = await request.body()
    form = parse_qs(body.decode())
    message = _first(form, "Body")
    resident_name = _first(form, "ProfileName") or "WhatsApp Resident"
    phone_number = _first(form, "From")

    if not message:
        raise HTTPException(status_code=400, detail="WhatsApp message body is required")

    payload = schemas.WhatsAppMessage(
        resident_name=resident_name,
        phone_number=phone_number,
        apartment_unit=_extract_unit(message),
        message=message,
    )
    complaint = _create_whatsapp_complaint(db, payload)
    return Response(
        content=_build_twiml_message(_build_whatsapp_reply(complaint)),
        media_type="application/xml",
    )


def _create_whatsapp_complaint(db: Session, payload: schemas.WhatsAppMessage):
    message = payload.message
    if payload.apartment_unit:
        message = f"Flat {payload.apartment_unit}: {message}"
    if payload.phone_number:
        message = f"{message}\nContact: {payload.phone_number}"

    complaint = SimpleNamespace(
        resident_name=payload.resident_name,
        message=message,
        category=None,
    )
    return crud.create_complaint(db=db, complaint=complaint)


def _build_whatsapp_reply(complaint):
    return (
        f"Complaint #{complaint.id} has been logged as {complaint.category} "
        f"with {complaint.priority.lower()} priority. Status: {complaint.status}. "
        "The apartment management team will update you soon."
    )


def _build_twiml_message(message: str):
    return f'<?xml version="1.0" encoding="UTF-8"?><Response><Message>{escape(message)}</Message></Response>'


def _first(form: dict[str, list[str]], key: str):
    value = form.get(key, [""])[0].strip()
    return value or None


def _extract_unit(message: str):
    words = message.replace(",", " ").split()
    for index, word in enumerate(words[:-1]):
        if word.lower() in {"flat", "unit", "apartment", "apt"}:
            return words[index + 1].strip("#:")
    return None
