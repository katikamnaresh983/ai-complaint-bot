from sqlalchemy.orm import Session
from . import models

def create_complaint(db: Session, complaint):
    db_complaint = models.Complaint(
        resident_name=complaint.resident_name,
        message=complaint.message
    )
    db.add(db_complaint)
    db.commit()
    db.refresh(db_complaint)
    return db_complaint
def get_complaints(db: Session):
    return db.query(models.Complaint).all()
def update_complaint_status(db: Session, complaint_id: int, status: str):
    complaint = db.query(models.Complaint).filter(models.Complaint.id == complaint_id).first()
    if complaint:
        complaint.status = status
        db.commit()
        db.refresh(complaint)
    return complaint