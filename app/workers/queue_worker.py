import asyncio
import httpx
import logging
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.queue_user import QueueUser, QueueUserStatus
from app.models.queue import Queue
from app.models.application import Application
from app.models.log import Log
from app.services.database import SessionLocal
from prometheus_client import Counter, Histogram, Gauge
import time

# Prometheus metrics
USERS_RELEASED = Counter('queue_users_released_total', 'Total users released from queue')
USERS_EXPIRED = Counter('queue_users_expired_total', 'Total users expired')
CALLBACK_SUCCESS = Counter('callback_success_total', 'Total successful callbacks')
CALLBACK_FAILURE = Counter('callback_failure_total', 'Total failed callbacks')
QUEUE_SIZE = Gauge('queue_size', 'Current queue size', ['queue_id'])
CALLBACK_DURATION = Histogram('callback_duration_seconds', 'Callback duration')

logger = logging.getLogger(__name__)

class QueueWorker:
    def __init__(self):
        self.running = False
        self.client = httpx.AsyncClient(timeout=30.0)

    async def start(self):
        """Start the background worker"""
        self.running = True
        logger.info("Queue worker started")
        while self.running:
            try:
                await self.process_queues()
                await self.cleanup_expired_tokens()
                await asyncio.sleep(60)  # Run every minute
            except Exception as e:
                logger.error(f"Error in queue worker: {e}")
                await asyncio.sleep(60)

    async def stop(self):
        """Stop the background worker"""
        self.running = False
        await self.client.aclose()
        logger.info("Queue worker stopped")

    async def process_queues(self):
        """Process all active queues and release users based on rate limits"""
        db = SessionLocal()
        try:
            queues = db.query(Queue).filter_by(is_active=True, is_deleted=False).all()
            for queue in queues:
                await self.process_queue(queue, db)
        finally:
            db.close()

    async def process_queue(self, queue: Queue, db: Session):
        """Process a single queue and release users based on max_users_per_minute"""
        # Get waiting users for this queue
        waiting_users = db.query(QueueUser).filter_by(
            queue_id=queue.id,
            status=QueueUserStatus.waiting,
            is_deleted=False
        ).order_by(QueueUser.created_at).limit(queue.max_users_per_minute).all()

        if not waiting_users:
            return

        # Update queue size metric
        total_waiting = db.query(QueueUser).filter_by(
            queue_id=queue.id,
            status=QueueUserStatus.waiting,
            is_deleted=False
        ).count()
        QUEUE_SIZE.labels(queue_id=str(queue.id)).set(total_waiting)

        # Release users
        for user in waiting_users:
            await self.release_user(user, queue, db)
            USERS_RELEASED.inc()

    async def release_user(self, user: QueueUser, queue: Queue, db: Session):
        """Release a user from the queue and send callback"""
        user.status = QueueUserStatus.ready
        user.wait_time = int((datetime.utcnow() - user.created_at).total_seconds())
        db.commit()

        # Send callback
        await self.send_callback(user, queue, db)

    async def send_callback(self, user: QueueUser, queue: Queue, db: Session):
        """Send callback to application with retry logic"""
        app = db.query(Application).filter_by(id=queue.application_id).first()
        if not app:
            logger.error(f"Application not found for queue {queue.id}")
            return

        callback_data = {
            "token": user.token,
            "visitor_id": user.visitor_id,
            "queue_id": str(queue.id),
            "status": user.status.value,
            "wait_time": user.wait_time,
            "redirect_url": user.redirect_url
        }

        start_time = time.time()
        success = False
        retries = 3

        for attempt in range(retries):
            try:
                response = await self.client.post(
                    app.callback_url,
                    json=callback_data,
                    headers={"Content-Type": "application/json"}
                )
                response.raise_for_status()
                success = True
                CALLBACK_SUCCESS.inc()
                break
            except Exception as e:
                logger.warning(f"Callback attempt {attempt + 1} failed for user {user.id}: {e}")
                if attempt < retries - 1:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff

        if not success:
            CALLBACK_FAILURE.inc()
            # Log the failure
            log = Log(
                event_type="callback_failure",
                message=f"Callback failed after {retries} attempts",
                details=f"User: {user.id}, Queue: {queue.id}, App: {app.id}",
                application_id=app.id,
                queue_id=queue.id,
                queue_user_id=user.id
            )
            db.add(log)
            db.commit()

        CALLBACK_DURATION.observe(time.time() - start_time)

    async def cleanup_expired_tokens(self):
        """Mark expired tokens as expired"""
        db = SessionLocal()
        try:
            expired_users = db.query(QueueUser).filter(
                QueueUser.status == QueueUserStatus.waiting,
                QueueUser.expires_at < datetime.utcnow(),
                QueueUser.is_deleted == False
            ).all()

            for user in expired_users:
                user.status = QueueUserStatus.expired
                USERS_EXPIRED.inc()

            db.commit()
            if expired_users:
                logger.info(f"Marked {len(expired_users)} users as expired")
        finally:
            db.close()

# Global worker instance
worker = QueueWorker()

async def start_worker():
    """Start the background worker"""
    await worker.start()

async def stop_worker():
    """Stop the background worker"""
    await worker.stop() 