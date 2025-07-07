from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from app.models.queue import Queue
from app.schemas.queue import QueueCreate, QueueUpdate, QueueResponse
from app.services.database import get_db

router = APIRouter(prefix="/queues", tags=["queues"])

@router.post("/", response_model=QueueResponse, status_code=status.HTTP_201_CREATED)
def create_queue(queue_in: QueueCreate, db: Session = Depends(get_db)):
    queue = Queue(**queue_in.dict())
    db.add(queue)
    db.commit()
    db.refresh(queue)
    return queue

@router.get("/", response_model=list[QueueResponse])
def list_queues(db: Session = Depends(get_db)):
    return db.query(Queue).filter_by(is_deleted=False).all()

@router.put("/{id}", response_model=QueueResponse)
def update_queue(id: UUID, queue_in: QueueUpdate, db: Session = Depends(get_db)):
    queue = db.query(Queue).filter_by(id=id, is_deleted=False).first()
    if not queue:
        raise HTTPException(status_code=404, detail="Queue not found")
    for k, v in queue_in.dict(exclude_unset=True).items():
        setattr(queue, k, v)
    db.commit()
    db.refresh(queue)
    return queue

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_queue(id: UUID, db: Session = Depends(get_db)):
    queue = db.query(Queue).filter_by(id=id, is_deleted=False).first()
    if not queue:
        raise HTTPException(status_code=404, detail="Queue not found")
    queue.is_deleted = True
    db.commit() 