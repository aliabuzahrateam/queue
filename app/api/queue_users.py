from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from uuid import UUID
from app.models.queue_user import QueueUser, QueueUserStatus
from app.models.queue import Queue
from app.models.application import Application
from app.schemas.queue_user import QueueUserCreate, QueueUserResponse, QueueUserJoin
from app.services.database import get_db
from datetime import datetime, timedelta
import uuid
from typing import List, Optional
from fastapi import Query

router = APIRouter(tags=["queue_users"])

@router.post("/join", response_model=QueueUserResponse)
def join_queue(
    queue_user_in: QueueUserJoin,
    request: Request,
    db: Session = Depends(get_db),
    mode: str = "real"
):
    api_key = request.headers.get("app_api_key")
    if not api_key:
        raise HTTPException(status_code=401, detail="Missing app_api_key")
    app = db.query(Application).filter_by(api_key=api_key, is_deleted=False).first()
    if not app:
        raise HTTPException(status_code=401, detail="Invalid app_api_key")
    queue = db.query(Queue).filter_by(id=queue_user_in.queue_id, application_id=app.id, is_deleted=False).first()
    if not queue:
        raise HTTPException(status_code=404, detail="Queue not found")
    if mode == "simulation":
        fake_token = uuid.uuid4().hex
        return QueueUserResponse(
            id=uuid.uuid4(),
            queue_id=queue.id,
            visitor_id=queue_user_in.visitor_id,
            status=QueueUserStatus.ready,
            token=fake_token,
            redirect_url=None,
            wait_time=0,
            expires_at=datetime.utcnow() + timedelta(minutes=5),
            created_at=datetime.utcnow()
        )
    # Real join
    token = uuid.uuid4().hex
    expires_at = datetime.utcnow() + timedelta(minutes=10)
    queue_user = QueueUser(
        queue_id=queue.id,
        visitor_id=queue_user_in.visitor_id,
        status=QueueUserStatus.waiting,
        token=token,
        expires_at=expires_at
    )
    db.add(queue_user)
    db.commit()
    db.refresh(queue_user)
    return queue_user

@router.get("/queue_status", response_model=QueueUserResponse)
def queue_status(token: str, db: Session = Depends(get_db)):
    queue_user = db.query(QueueUser).filter_by(token=token, is_deleted=False).first()
    if not queue_user:
        raise HTTPException(status_code=404, detail="Token not found")
    return queue_user

@router.get("/queue_users", response_model=List[QueueUserResponse])
def list_queue_users(
    queue_id: UUID,
    status: Optional[QueueUserStatus] = Query(None),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    query = db.query(QueueUser).filter_by(queue_id=queue_id, is_deleted=False)
    if status:
        query = query.filter_by(status=status)
    return query.offset(skip).limit(limit).all()

@router.post("/cancel", status_code=status.HTTP_204_NO_CONTENT)
def cancel_queue(token: str, db: Session = Depends(get_db)):
    queue_user = db.query(QueueUser).filter_by(token=token, is_deleted=False).first()
    if not queue_user:
        raise HTTPException(status_code=404, detail="Token not found")
    queue_user.status = QueueUserStatus.rejected
    queue_user.is_deleted = True
    db.commit() 