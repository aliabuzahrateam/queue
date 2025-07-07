from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from app.models.application import Application
from app.schemas.application import ApplicationCreate, ApplicationUpdate, ApplicationResponse
from app.services.database import get_db
import uuid

router = APIRouter(prefix="/applications", tags=["applications"])

@router.post("/", response_model=ApplicationResponse, status_code=status.HTTP_201_CREATED)
def create_application(app_in: ApplicationCreate, db: Session = Depends(get_db)):
    api_key = uuid.uuid4().hex
    app = Application(**app_in.dict(), api_key=api_key)
    db.add(app)
    db.commit()
    db.refresh(app)
    return app

@router.get("/", response_model=list[ApplicationResponse])
def list_applications(db: Session = Depends(get_db)):
    return db.query(Application).filter_by(is_deleted=False).all()

@router.get("/{id}", response_model=ApplicationResponse)
def get_application(id: UUID, db: Session = Depends(get_db)):
    app = db.query(Application).filter_by(id=id, is_deleted=False).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    return app

@router.put("/{id}", response_model=ApplicationResponse)
def update_application(id: UUID, app_in: ApplicationUpdate, db: Session = Depends(get_db)):
    app = db.query(Application).filter_by(id=id, is_deleted=False).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    for k, v in app_in.dict(exclude_unset=True).items():
        setattr(app, k, v)
    db.commit()
    db.refresh(app)
    return app

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_application(id: UUID, db: Session = Depends(get_db)):
    app = db.query(Application).filter_by(id=id, is_deleted=False).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    app.is_deleted = True 