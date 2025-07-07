# 🚀 Queue Management System - Complete Startup Guide

This guide covers everything you need to get the Queue Management System up and running, including all the missing components we've just added.

## 📋 What Was Missing (Now Fixed!)

### ✅ **Added Components:**

1. **Database Migration System** - Alembic configuration and environment
2. **Authentication API** - Login, token refresh, user management
3. **Rate Limiting Middleware** - API protection from abuse
4. **CORS Configuration** - Cross-origin request support
5. **Error Handling Middleware** - Consistent error responses and logging
6. **Additional Tests** - Worker functionality testing
7. **Database Initialization Script** - Automated setup
8. **Enhanced Main Application** - All middleware and routers integrated

## 🛠️ **Complete Setup Process**

### **Step 1: Environment Configuration**

```bash
# Run the interactive setup script
cd queue
python setup_env.py
```

Or manually create `.env` file:

```bash
# Database Configuration
DB_URL=postgresql+psycopg2://queue_user:queue_password@db:5432/queue_db

# Prometheus Configuration
PROMETHEUS_MULTIPROC_DIR=/tmp

# Admin Configuration
ADMIN_EMAIL=admin@yourcompany.com
ADMIN_PASSWORD=changeme123

# Security Configuration
SECRET_KEY=your-super-secret-key-change-this-in-production

# Queue Configuration
QUEUE_THRESHOLD=100

# SMTP Configuration (Optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASS=your-app-password

# Webhook Configuration (Optional)
WEBHOOK_URL=https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK

# CORS Configuration (Optional)
ALLOWED_ORIGINS=*

# Rate Limiting (Optional)
RATE_LIMIT_PER_MINUTE=1000
```

### **Step 2: Database Setup**

```bash
# Initialize database with sample data
python scripts/init_db.py
```

This will:
- ✅ Create all database tables
- ✅ Run Alembic migrations
- ✅ Create sample application and queue
- ✅ Generate sample API key for testing

### **Step 3: Start the System**

```bash
# Start all services with Docker Compose
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f fastapi
```

### **Step 4: Verify Installation**

```bash
# Check API health
curl http://localhost:8000/health

# Check system info
curl http://localhost:8000/info

# Access API documentation
open http://localhost:8000/docs
```

## 🔧 **New Features & Endpoints**

### **Authentication API (`/auth`)**
- `POST /auth/login` - Login with email/password or API key
- `GET /auth/me` - Get current user information
- `POST /auth/refresh` - Refresh access token
- `GET /auth/health` - Authentication service health

### **Enhanced Security**
- **Rate Limiting**: 1000 requests per minute per client
- **CORS Support**: Configurable cross-origin requests
- **Error Handling**: Consistent error responses
- **Request Logging**: Comprehensive request/response logging

### **Database Migrations**
```bash
# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

## 🧪 **Testing the System**

### **Run All Tests**
```bash
# Run all tests with coverage
pytest tests/ -v --cov=app --cov-report=html

# Run specific test files
pytest tests/test_api.py -v
pytest tests/test_worker.py -v

# Run tests with specific markers
pytest tests/ -m "not slow"
```

### **Manual Testing**

1. **Create Application:**
```bash
curl -X POST "http://localhost:8000/applications/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test App",
    "domain": "test.com",
    "callback_url": "https://test.com/callback"
  }'
```

2. **Join Queue:**
```bash
curl -X POST "http://localhost:8000/join" \
  -H "Content-Type: application/json" \
  -H "app_api_key: sample-api-key-123" \
  -d '{
    "queue_id": "your-queue-id",
    "visitor_id": "visitor123"
  }'
```

3. **Check Queue Status:**
```bash
curl "http://localhost:8000/queue_status?token=your-token"
```

## 📊 **Monitoring & Analytics**

### **Prometheus Metrics**
- Access: http://localhost:9090
- Metrics endpoint: http://localhost:8000/metrics

### **Grafana Dashboards**
- Access: http://localhost:3000
- Default credentials: admin/admin
- Import dashboards from `docs/grafana-queries.md`

### **System Health**
```bash
# Check all services
curl http://localhost:8000/health

# Check specific service
curl http://localhost:8000/auth/health
```

## 🔍 **Troubleshooting**

### **Common Issues**

1. **Database Connection Failed**
```bash
# Check if SQL Server is running
docker-compose ps db

# Check database logs
docker-compose logs db

# Test connection manually
python scripts/init_db.py
```

2. **Rate Limiting Issues**
```bash
# Check rate limit headers in response
curl -I http://localhost:8000/applications/

# Adjust rate limit in .env
RATE_LIMIT_PER_MINUTE=2000
```

3. **Authentication Issues**
```bash
# Test login
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@yourcompany.com&password=changeme123"
```

4. **Worker Not Processing**
```bash
# Check worker logs
docker-compose logs fastapi | grep worker

# Check queue status
curl http://localhost:8000/dashboard/summary
```

### **Logs and Debugging**

```bash
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f fastapi
docker-compose logs -f db

# Check application logs
tail -f queue_system.log
```

## 🚀 **Production Deployment**

### **Environment Variables for Production**
```bash
# Use strong secrets
SECRET_KEY=your-production-secret-key
ADMIN_PASSWORD=strong-production-password

# Configure proper database
DB_URL=mssql+pyodbc://produser:prodpass@prod-db:1433/queue_db_prod

# Set up monitoring
PROMETHEUS_MULTIPROC_DIR=/tmp
QUEUE_THRESHOLD=500

# Configure alerts
SMTP_HOST=your-smtp-server.com
WEBHOOK_URL=https://your-slack-webhook.com
```

### **Security Checklist**
- [ ] Change default passwords
- [ ] Use strong SECRET_KEY
- [ ] Configure proper CORS origins
- [ ] Set up SSL/TLS
- [ ] Enable database encryption
- [ ] Configure firewall rules
- [ ] Set up monitoring alerts

## 📚 **API Documentation**

### **Complete API Reference**
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

### **Authentication**
- **API Key**: Use `app_api_key` header for queue operations
- **JWT Token**: Use `Authorization: Bearer <token>` for admin operations

### **Rate Limiting**
- **Limit**: 1000 requests per minute per client
- **Headers**: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`

## 🎉 **Success Indicators**

Your system is fully operational when:

✅ **All services are running:**
```bash
docker-compose ps
# All services should show "Up" status
```

✅ **API responds correctly:**
```bash
curl http://localhost:8000/health
# Should return {"status": "healthy"}
```

✅ **Database is accessible:**
```bash
curl http://localhost:8000/applications/
# Should return list of applications
```

✅ **Worker is processing:**
```bash
curl http://localhost:8000/dashboard/summary
# Should show queue statistics
```

✅ **Monitoring is working:**
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000
- Metrics: http://localhost:8000/metrics

## 🔄 **Next Steps**

1. **Customize Configuration**: Update `.env` for your environment
2. **Add Applications**: Create your first application via API
3. **Set Up Monitoring**: Configure Grafana dashboards
4. **Configure Alerts**: Set up email/webhook notifications
5. **Scale Up**: Add more workers or services as needed
6. **Backup Strategy**: Implement database backups
7. **Security Audit**: Review and harden security settings

## 📞 **Support**

If you encounter issues:

1. Check the logs: `docker-compose logs -f`
2. Review this guide and `CONFIGURATION_GUIDE.md`
3. Check the API documentation: http://localhost:8000/docs
4. Review the project summary: `PROJECT_SUMMARY.md`

**Congratulations!** Your Queue Management System is now complete and production-ready! 🎉 