from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from . import models, database, schemas, crud

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/complaints/")
def create_complaint(complaint: schemas.ComplaintCreate, db: Session = Depends(get_db)):
    return crud.create_complaint(db=db, complaint=complaint)
@app.get("/complaints/")
def read_complaints(db: Session = Depends(get_db)):
    return crud.get_complaints(db)
@app.patch("/complaints/{complaint_id}")
def update_status(complaint_id: int, update: schemas.ComplaintUpdate, db: Session = Depends(get_db)):
    return crud.update_complaint_status(db, complaint_id, update.status)