from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from uuid import UUID
from datetime import datetime, timedelta
from app.models.queue_user import QueueUser, QueueUserStatus
from app.models.queue import Queue
from app.models.application import Application
from app.models.log import Log
from app.services.database import get_db
from typing import Optional, Dict, Any

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

@router.get("/summary")
def get_summary(db: Session = Depends(get_db)):
    """Get overall system summary"""
    total_apps = db.query(Application).filter_by(is_deleted=False).count()
    total_queues = db.query(Queue).filter_by(is_deleted=False).count()
    
    # User statistics
    total_users = db.query(QueueUser).filter_by(is_deleted=False).count()
    waiting_users = db.query(QueueUser).filter_by(
        status=QueueUserStatus.waiting, 
        is_deleted=False
    ).count()
    ready_users = db.query(QueueUser).filter_by(
        status=QueueUserStatus.ready, 
        is_deleted=False
    ).count()
    expired_users = db.query(QueueUser).filter_by(
        status=QueueUserStatus.expired, 
        is_deleted=False
    ).count()
    rejected_users = db.query(QueueUser).filter_by(
        status=QueueUserStatus.rejected, 
        is_deleted=False
    ).count()

    # Average wait time
    avg_wait_time = db.query(func.avg(QueueUser.wait_time)).filter(
        QueueUser.wait_time.isnot(None),
        QueueUser.is_deleted == False
    ).scalar() or 0

    return {
        "applications": total_apps,
        "queues": total_queues,
        "total_users": total_users,
        "waiting_users": waiting_users,
        "ready_users": ready_users,
        "expired_users": expired_users,
        "rejected_users": rejected_users,
        "average_wait_time_seconds": float(avg_wait_time)
    }

@router.get("/queue_stats")
def get_queue_stats(db: Session = Depends(get_db)):
    """Get statistics for all queues"""
    queues = db.query(Queue).filter_by(is_deleted=False).all()
    stats = []
    
    for queue in queues:
        waiting_count = db.query(QueueUser).filter_by(
            queue_id=queue.id,
            status=QueueUserStatus.waiting,
            is_deleted=False
        ).count()
        
        ready_count = db.query(QueueUser).filter_by(
            queue_id=queue.id,
            status=QueueUserStatus.ready,
            is_deleted=False
        ).count()
        
        avg_wait_time = db.query(func.avg(QueueUser.wait_time)).filter(
            QueueUser.queue_id == queue.id,
            QueueUser.wait_time.isnot(None),
            QueueUser.is_deleted == False
        ).scalar() or 0
        
        stats.append({
            "queue_id": str(queue.id),
            "queue_name": queue.name,
            "max_users_per_minute": queue.max_users_per_minute,
            "priority": queue.priority,
            "waiting_users": waiting_count,
            "ready_users": ready_count,
            "average_wait_time_seconds": float(avg_wait_time)
        })
    
    return stats

@router.get("/callback_errors")
def get_callback_errors(
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get recent callback errors"""
    errors = db.query(Log).filter_by(
        event_type="callback_failure"
    ).order_by(Log.created_at.desc()).limit(limit).all()
    
    return [
        {
            "id": str(error.id),
            "message": error.message,
            "details": error.details,
            "created_at": error.created_at,
            "application_id": str(error.application_id) if error.application_id else None,
            "queue_id": str(error.queue_id) if error.queue_id else None
        }
        for error in errors
    ]

@router.get("/analytics")
def get_analytics(
    app_id: Optional[UUID] = Query(None),
    days: int = Query(7, ge=1, le=30),
    db: Session = Depends(get_db)
):
    """Get analytics for applications or specific app"""
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # Base query filter
    base_filter = and_(
        QueueUser.created_at >= start_date,
        QueueUser.created_at <= end_date,
        QueueUser.is_deleted == False
    )
    
    if app_id:
        # Get queues for specific app
        queue_ids = [q.id for q in db.query(Queue).filter_by(
            application_id=app_id, 
            is_deleted=False
        ).all()]
        base_filter = and_(base_filter, QueueUser.queue_id.in_(queue_ids))
    
    # Daily user joins
    daily_joins = db.query(
        func.date(QueueUser.created_at).label('date'),
        func.count(QueueUser.id).label('count')
    ).filter(base_filter).group_by(
        func.date(QueueUser.created_at)
    ).order_by(func.date(QueueUser.created_at)).all()
    
    # Status distribution
    status_counts = db.query(
        QueueUser.status,
        func.count(QueueUser.id).label('count')
    ).filter(base_filter).group_by(QueueUser.status).all()
    
    # Completion rate
    total_users = db.query(QueueUser).filter(base_filter).count()
    completed_users = db.query(QueueUser).filter(
        base_filter,
        QueueUser.status == QueueUserStatus.ready
    ).count()
    
    completion_rate = (completed_users / total_users * 100) if total_users > 0 else 0
    
    # Average wait time by day
    daily_wait_times = db.query(
        func.date(QueueUser.created_at).label('date'),
        func.avg(QueueUser.wait_time).label('avg_wait_time')
    ).filter(
        base_filter,
        QueueUser.wait_time.isnot(None)
    ).group_by(
        func.date(QueueUser.created_at)
    ).order_by(func.date(QueueUser.created_at)).all()
    
    return {
        "period": {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "days": days
        },
        "daily_joins": [
            {"date": str(day.date), "count": day.count}
            for day in daily_joins
        ],
        "status_distribution": [
            {"status": status.status.value, "count": status.count}
            for status in status_counts
        ],
        "completion_rate_percent": round(completion_rate, 2),
        "daily_wait_times": [
            {"date": str(day.date), "avg_wait_time_seconds": float(day.avg_wait_time or 0)}
            for day in daily_wait_times
        ]
    } 