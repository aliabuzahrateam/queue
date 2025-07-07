# Configuration Guide - Environment Variables Setup

This guide will help you configure the environment variables for the Queue Management System.

## 🚀 Quick Setup

### 1. Create `.env` file

Create a `.env` file in the root directory (`queue/`) with the following content:

```bash
# Database Configuration
DB_URL=postgresql+psycopg2://queue_user:queue_password@db:5432/queue_db

# Prometheus Configuration
PROMETHEUS_MULTIPROC_DIR=/tmp

# Admin Configuration
ADMIN_EMAIL=admin@yourcompany.com
ADMIN_PASSWORD=changeme123

# SMTP Configuration (for email alerts)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASS=your-app-password

# Webhook Configuration (for Slack/Teams alerts)
WEBHOOK_URL=https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK

# Security Configuration
SECRET_KEY=your-super-secret-key-change-this-in-production

# Queue Configuration
QUEUE_THRESHOLD=100
```

## 🔧 Detailed Configuration

### Database Configuration

**DB_URL**: PostgreSQL connection string

```bash
# Format:
DB_URL=postgresql+psycopg2://username:password@host:port/database

# For Docker Compose (default):
DB_URL=postgresql+psycopg2://queue_user:queue_password@db:5432/queue_db

# For local PostgreSQL:
DB_URL=postgresql+psycopg2://queue_user:queue_password@db:5432/queue_db
```

### SMTP Configuration (Email Alerts)

**For Gmail:**
```bash
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASS=your-app-password  # Use App Password, not regular password
```

**For Outlook/Hotmail:**
```bash
SMTP_HOST=smtp-mail.outlook.com
SMTP_PORT=587
SMTP_USER=your-email@outlook.com
SMTP_PASS=your-password
```

**For Custom SMTP Server:**
```bash
SMTP_HOST=your-smtp-server.com
SMTP_PORT=587  # or 465 for SSL
SMTP_USER=your-username
SMTP_PASS=your-password
```

### Webhook Configuration (Slack/Teams Alerts)

**For Slack:**
1. Go to your Slack workspace
2. Create a new app or use existing one
3. Enable Incoming Webhooks
4. Create a webhook for your channel
5. Copy the webhook URL

```bash
WEBHOOK_URL=https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX
```

**For Microsoft Teams:**
1. Go to your Teams channel
2. Click the "..." menu
3. Select "Connectors"
4. Configure Incoming Webhook
5. Copy the webhook URL

```bash
WEBHOOK_URL=https://your-org.webhook.office.com/webhookb2/xxx/IncomingWebhook/xxx/xxx
```

### Security Configuration

**SECRET_KEY**: Generate a strong random key

```bash
# Generate a secure key (run this in Python):
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Example output:
SECRET_KEY=your-generated-secret-key-here
```

### Queue Configuration

**QUEUE_THRESHOLD**: Maximum queue size before alerts

```bash
# Alert when any queue has more than 100 users
QUEUE_THRESHOLD=100

# For high-traffic applications
QUEUE_THRESHOLD=500

# For low-traffic applications
QUEUE_THRESHOLD=50
```

## 🔐 Security Best Practices

### 1. Generate Strong Secrets

```bash
# Generate SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Generate strong password
python -c "import secrets; import string; print(''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(16)))"
```

### 2. Use Environment-Specific Configurations

**Development:**
```bash
DB_URL=postgresql+psycopg2://queue_user:devpassword@db:5432/queue_db_dev
SECRET_KEY=dev-secret-key
QUEUE_THRESHOLD=50
```

**Staging:**
```bash
DB_URL=postgresql+psycopg2://queue_user:stagingpassword@db:5432/queue_db_staging
SECRET_KEY=staging-secret-key
QUEUE_THRESHOLD=100
```

**Production:**
```bash
DB_URL=postgresql+psycopg2://queue_user:prodpassword@db:5432/queue_db_prod
SECRET_KEY=production-secret-key
QUEUE_THRESHOLD=200
```

### 3. Secure Database Credentials

- Use strong passwords for database users
- Create dedicated database users with minimal permissions
- Use connection pooling in production
- Enable SSL/TLS for database connections

## 🧪 Testing Configuration

### 1. Test Database Connection

```bash
# Test with Python
python -c "
import os
from dotenv import load_dotenv
load_dotenv()
print('DB_URL:', os.getenv('DB_URL'))
"
```

### 2. Test SMTP Configuration

```bash
# Test email sending
python -c "
import smtplib
from email.mime.text import MIMEText
import os
from dotenv import load_dotenv

load_dotenv()

try:
    server = smtplib.SMTP(os.getenv('SMTP_HOST'), int(os.getenv('SMTP_PORT')))
    server.starttls()
    server.login(os.getenv('SMTP_USER'), os.getenv('SMTP_PASS'))
    print('SMTP configuration is working!')
    server.quit()
except Exception as e:
    print('SMTP configuration error:', e)
"
```

### 3. Test Webhook Configuration

```bash
# Test webhook (replace with your actual webhook URL)
curl -X POST -H 'Content-type: application/json' \
  --data '{\"text\":\"Test message from Queue Management System\"}' \
  https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK
```

## 🚀 Deployment Configuration

### Docker Compose (Recommended)

The `docker-compose.yml` file is already configured to use the `.env` file:

```yaml
services:
  fastapi:
    env_file:
      - .env
```

### Kubernetes

For Kubernetes deployment, create a ConfigMap and Secret:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: queue-config
data:
  QUEUE_THRESHOLD: "100"
  PROMETHEUS_MULTIPROC_DIR: "/tmp"
  SMTP_HOST: "smtp.gmail.com"
  SMTP_PORT: "587"
---
apiVersion: v1
kind: Secret
metadata:
  name: queue-secrets
type: Opaque
data:
  DB_URL: <base64-encoded-db-url>
  SECRET_KEY: <base64-encoded-secret-key>
  SMTP_USER: <base64-encoded-smtp-user>
  SMTP_PASS: <base64-encoded-smtp-password>
  WEBHOOK_URL: <base64-encoded-webhook-url>
```

## 🔍 Troubleshooting

### Common Issues

1. **Database Connection Failed**
   - Check if SQL Server is running
   - Verify connection string format
   - Ensure ODBC driver is installed

2. **SMTP Authentication Failed**
   - Use App Password for Gmail
   - Check if 2FA is enabled
   - Verify SMTP settings

3. **Webhook Not Working**
   - Check webhook URL format
   - Verify webhook is active
   - Test with curl command

4. **Permission Denied**
   - Check file permissions for `.env`
   - Ensure Docker has access to the file
   - Verify user permissions

### Validation Commands

```bash
# Check if .env file exists and is readable
ls -la .env

# Validate environment variables are loaded
python -c "
import os
from dotenv import load_dotenv
load_dotenv()
required_vars = ['DB_URL', 'SECRET_KEY', 'ADMIN_EMAIL']
for var in required_vars:
    value = os.getenv(var)
    print(f'{var}: {\"✓\" if value else \"✗\"}')
"
```

## 📋 Configuration Checklist

- [ ] Database connection string configured
- [ ] Secret key generated and set
- [ ] Admin email configured
- [ ] SMTP settings configured (optional)
- [ ] Webhook URL configured (optional)
- [ ] Queue threshold set
- [ ] Environment variables tested
- [ ] Security best practices followed

Once you've completed this configuration, you can start the system with:

```bash
docker-compose up -d
```

The system will be available at:
- **API**: http://localhost:8000
- **Documentation**: http://localhost:8000/docs
- **Grafana**: http://localhost:3000
- **Prometheus**: http://localhost:9090 