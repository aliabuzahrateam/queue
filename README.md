# Queue Management System

A production-ready FastAPI-based queue management system with Microsoft SQL Server, supporting multiple client applications with rate-controlled user release, monitoring, and analytics.

## 🚀 Features

- **Multi-tenant Architecture**: Support for multiple applications with isolated queues
- **Rate-controlled Release**: Configurable user release rates per queue
- **Background Worker**: Automated queue processing with callback notifications
- **Prometheus Monitoring**: Real-time metrics and Grafana dashboards
- **Dynamic JS Client**: Configurable JavaScript integration for websites
- **Admin Dashboard**: Analytics and monitoring endpoints
- **Authentication**: OAuth2 and API key-based authentication
- **Alerts**: Email and webhook notifications for queue events
- **Localization**: Multi-language support (English, Arabic)
- **Simulation Mode**: Testing capabilities without affecting real queues
- **Docker Support**: Complete containerized deployment

## 📋 Prerequisites

- Python 3.11+
- Microsoft SQL Server 2022
- Docker and Docker Compose
- Prometheus and Grafana (included in docker-compose)

## 🛠️ Installation

### 1. Clone the repository
```bash
git clone <repository-url>
cd queue
```

### 2. Set up environment variables
```bash
cp .env.example .env
# Edit .env with your configuration
```

### 3. Run with Docker Compose
```bash
docker-compose up -d
```

### 4. Manual setup (alternative)
```bash
# Install dependencies
pip install -r requirements.txt

# Set up database
# Create MSSQL database and update DB_URL in .env

# Run migrations (if using Alembic)
alembic upgrade head

# Start the application
uvicorn app.main:app --reload
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DB_URL` | SQL Server connection string | Required |
| `SECRET_KEY` | JWT secret key | Required |
| `ADMIN_EMAIL` | Admin email for alerts | Required |
| `SMTP_HOST` | SMTP server host | Optional |
| `SMTP_PORT` | SMTP server port | 587 |
| `SMTP_USER` | SMTP username | Optional |
| `SMTP_PASS` | SMTP password | Optional |
| `WEBHOOK_URL` | Slack/Teams webhook URL | Optional |
| `QUEUE_THRESHOLD` | Queue length alert threshold | 100 |

## 📚 API Documentation

### Applications

```bash
# Create application
POST /applications/
{
  "name": "My App",
  "domain": "myapp.com",
  "callback_url": "https://myapp.com/callback"
}

# List applications
GET /applications/

# Get application
GET /applications/{id}

# Update application
PUT /applications/{id}

# Delete application (soft delete)
DELETE /applications/{id}
```

### Queues

```bash
# Create queue
POST /queues/
{
  "application_id": "uuid",
  "name": "Main Queue",
  "max_users_per_minute": 10,
  "priority": 1
}

# List queues
GET /queues/

# Update queue
PUT /queues/{id}

# Delete queue
DELETE /queues/{id}
```

### Queue Users

```bash
# Join queue
POST /join
Headers: app_api_key: your-api-key
{
  "queue_id": "uuid",
  "visitor_id": "visitor123"
}

# Check queue status
GET /queue_status?token=user-token

# Cancel queue
POST /cancel?token=user-token
```

### Dashboard

```bash
# System summary
GET /dashboard/summary

# Queue statistics
GET /dashboard/queue_stats

# Callback errors
GET /dashboard/callback_errors

# Analytics
GET /dashboard/analytics?app_id=uuid&days=7
```

## 🌐 JavaScript Integration

### Basic Integration

```html
<script src="http://your-domain/scripts/queue.js?app_id=your-app-id&callback_url=https://your-site.com/ready"></script>

<script>
// Auto-initialization with URL parameters
// ?queue_id=uuid&visitor_id=visitor123
</script>
```

### Advanced Integration

```javascript
const queueManager = new QueueManager({
    apiKey: 'your-api-key',
    callbackUrl: 'https://your-site.com/ready',
    lang: 'en',
    theme: 'light'
});

// Join queue
queueManager.joinQueue('queue-uuid', 'visitor123');

// Cancel queue
queueManager.cancel();
```

## 📊 Monitoring

### Prometheus Metrics

- `queue_users_released_total`: Total users released from queue
- `queue_users_expired_total`: Total users expired
- `callback_success_total`: Total successful callbacks
- `callback_failure_total`: Total failed callbacks
- `queue_size`: Current queue size per queue
- `callback_duration_seconds`: Callback duration histogram

### Grafana Dashboards

Access Grafana at `http://localhost:3000` and import the provided dashboard templates.

## 🔔 Alerts

The system sends alerts for:

- Queue length exceeding threshold
- Callback failures after retries
- System health issues

Configure alerts via:
- Email (SMTP)
- Webhooks (Slack/Teams)

## 🧪 Testing

```bash
# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html

# Run specific test file
pytest tests/test_api.py -v
```

## 🚀 Deployment

### Docker Deployment

```bash
# Build and run
docker-compose up -d

# View logs
docker-compose logs -f fastapi

# Scale workers
docker-compose up -d --scale worker=3
```

### Kubernetes Deployment

```bash
# Apply Kubernetes manifests
kubectl apply -f k8s/

# Check deployment status
kubectl get pods -l app=queue-management
```

## 🔒 Security

- API key authentication for queue operations
- JWT tokens for admin access
- Role-based access control
- Input validation and sanitization
- Rate limiting (configurable)

## 🌍 Localization

Supported languages:
- English (en)
- Arabic (ar)

Configure via URL parameters or JavaScript options.

## 📈 Performance

- Connection pooling for database
- Async background workers
- Prometheus metrics for monitoring
- Configurable rate limits
- Efficient queue processing

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue on GitHub
- Check the API documentation at `/docs`
- Review the logs for debugging information 