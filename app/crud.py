from sqlalchemy.orm import Session

from . import ai, models


def build_complaint_record(complaint):
    analysis = ai.analyze_complaint(complaint.message, complaint.category)
    return models.Complaint(
        resident_name=complaint.resident_name,
        message=complaint.message,
        category=analysis.category,
        priority=analysis.priority,
        sentiment=analysis.sentiment,
        summary=analysis.summary,
        suggested_response=analysis.suggested_response,
    )


def create_complaint(db: Session, complaint):
    db_complaint = build_complaint_record(complaint)
    db.add(db_complaint)
    db.commit()
    db.refresh(db_complaint)
    return db_complaint


def get_complaints(db: Session):
    return db.query(models.Complaint).order_by(models.Complaint.id.desc()).all()


def get_complaint(db: Session, complaint_id: int):
    return db.query(models.Complaint).filter(models.Complaint.id == complaint_id).first()


def update_complaint_status(db: Session, complaint_id: int, status: str):
    complaint = get_complaint(db, complaint_id)
    if complaint:
        complaint.status = status
        db.commit()
        db.refresh(complaint)
    return complaint


def update_complaint_category(db: Session, complaint_id: int, category: str):
    complaint = get_complaint(db, complaint_id)
    if complaint:
        complaint.category = category
        db.commit()
        db.refresh(complaint)
    return complaint


def get_dashboard_stats(db: Session):
    complaints = db.query(models.Complaint).all()
    statuses = {status: 0 for status in ["Open", "In Progress", "Resolved", "Closed"]}
    categories = {}
    priorities = {}

    for complaint in complaints:
        statuses[complaint.status] = statuses.get(complaint.status, 0) + 1
        categories[complaint.category] = categories.get(complaint.category, 0) + 1
        priorities[complaint.priority] = priorities.get(complaint.priority, 0) + 1

    return {
        "total": len(complaints),
        "open": statuses.get("Open", 0),
        "in_progress": statuses.get("In Progress", 0),
        "resolved": statuses.get("Resolved", 0) + statuses.get("Closed", 0),
        "urgent": priorities.get("Urgent", 0),
        "categories": categories,
        "priorities": priorities,
    }
