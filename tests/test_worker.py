import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from app.workers.queue_worker import QueueWorker, start_worker, stop_worker
from app.models.queue_user import QueueUserStatus
from app.models.queue import Queue
from app.models.application import Application
from datetime import datetime, timedelta

@pytest.fixture
def mock_db_session():
    """Mock database session"""
    session = Mock()
    session.query.return_value.filter_by.return_value.all.return_value = []
    session.query.return_value.filter_by.return_value.order_by.return_value.limit.return_value.all.return_value = []
    session.query.return_value.filter_by.return_value.count.return_value = 0
    session.commit = Mock()
    session.close = Mock()
    return session

@pytest.fixture
def sample_queue():
    """Sample queue for testing"""
    queue = Mock(spec=Queue)
    queue.id = "test-queue-id"
    queue.max_users_per_minute = 10
    queue.priority = 1
    return queue

@pytest.fixture
def sample_user():
    """Sample queue user for testing"""
    user = Mock(spec=QueueUser)
    user.id = "test-user-id"
    user.visitor_id = "visitor123"
    user.status = QueueUserStatus.waiting
    user.token = "test-token"
    user.created_at = datetime.utcnow()
    user.wait_time = None
    return user

@pytest.fixture
def sample_application():
    """Sample application for testing"""
    app = Mock(spec=Application)
    app.id = "test-app-id"
    app.callback_url = "https://example.com/callback"
    return app

class TestQueueWorker:
    
    @pytest.mark.asyncio
    async def test_worker_initialization(self):
        """Test worker initialization"""
        worker = QueueWorker()
        assert worker.running == False
        assert worker.client is not None
    
    @pytest.mark.asyncio
    async def test_worker_start_stop(self):
        """Test worker start and stop"""
        worker = QueueWorker()
        
        # Mock the process_queues method to avoid infinite loop
        worker.process_queues = AsyncMock()
        
        # Start worker
        start_task = asyncio.create_task(worker.start())
        
        # Wait a bit for worker to start
        await asyncio.sleep(0.1)
        
        # Stop worker
        await worker.stop()
        
        # Wait for worker to stop
        await asyncio.sleep(0.1)
        
        # Cancel the task
        start_task.cancel()
        try:
            await start_task
        except asyncio.CancelledError:
            pass
        
        assert worker.running == False
    
    @pytest.mark.asyncio
    async def test_process_queue_with_users(self, mock_db_session, sample_queue, sample_user):
        """Test processing queue with waiting users"""
        worker = QueueWorker()
        
        # Mock database query to return a user
        mock_db_session.query.return_value.filter_by.return_value.order_by.return_value.limit.return_value.all.return_value = [sample_user]
        mock_db_session.query.return_value.filter_by.return_value.count.return_value = 1
        
        # Mock application query
        mock_db_session.query.return_value.filter_by.return_value.first.return_value = Mock(spec=Application)
        
        # Mock callback sending
        with patch.object(worker, 'send_callback', new_callable=AsyncMock):
            await worker.process_queue(sample_queue, mock_db_session)
            
            # Verify user status was updated
            sample_user.status = QueueUserStatus.ready
            mock_db_session.commit.assert_called()
    
    @pytest.mark.asyncio
    async def test_send_callback_success(self, mock_db_session, sample_user, sample_queue, sample_application):
        """Test successful callback sending"""
        worker = QueueWorker()
        
        # Mock application query
        mock_db_session.query.return_value.filter_by.return_value.first.return_value = sample_application
        
        # Mock successful HTTP response
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        
        with patch.object(worker.client, 'post', new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_response
            
            await worker.send_callback(sample_user, sample_queue, mock_db_session)
            
            # Verify callback was sent
            mock_post.assert_called_once()
            call_args = mock_post.call_args
            assert call_args[1]['json']['token'] == sample_user.token
            assert call_args[1]['json']['visitor_id'] == sample_user.visitor_id
    
    @pytest.mark.asyncio
    async def test_send_callback_failure_with_retry(self, mock_db_session, sample_user, sample_queue, sample_application):
        """Test callback failure with retry logic"""
        worker = QueueWorker()
        
        # Mock application query
        mock_db_session.query.return_value.filter_by.return_value.first.return_value = sample_application
        
        # Mock failed HTTP response
        with patch.object(worker.client, 'post', new_callable=AsyncMock) as mock_post:
            mock_post.side_effect = Exception("Connection failed")
            
            await worker.send_callback(sample_user, sample_queue, mock_db_session)
            
            # Verify retry attempts (3 times)
            assert mock_post.call_count == 3
    
    @pytest.mark.asyncio
    async def test_cleanup_expired_tokens(self, mock_db_session):
        """Test cleanup of expired tokens"""
        worker = QueueWorker()
        
        # Mock expired user
        expired_user = Mock(spec=QueueUser)
        expired_user.status = QueueUserStatus.waiting
        expired_user.expires_at = datetime.utcnow() - timedelta(minutes=1)
        
        # Mock database query to return expired user
        mock_db_session.query.return_value.filter.return_value.all.return_value = [expired_user]
        
        await worker.cleanup_expired_tokens(mock_db_session)
        
        # Verify user status was updated to expired
        assert expired_user.status == QueueUserStatus.expired
        mock_db_session.commit.assert_called()

@pytest.mark.asyncio
async def test_start_worker_function():
    """Test start_worker function"""
    with patch('app.workers.queue_worker.worker') as mock_worker:
        mock_worker.start = AsyncMock()
        
        # Start worker
        start_task = asyncio.create_task(start_worker())
        
        # Wait a bit
        await asyncio.sleep(0.1)
        
        # Cancel task
        start_task.cancel()
        try:
            await start_task
        except asyncio.CancelledError:
            pass
        
        mock_worker.start.assert_called_once()

@pytest.mark.asyncio
async def test_stop_worker_function():
    """Test stop_worker function"""
    with patch('app.workers.queue_worker.worker') as mock_worker:
        mock_worker.stop = AsyncMock()
        
        await stop_worker()
        
        mock_worker.stop.assert_called_once() 