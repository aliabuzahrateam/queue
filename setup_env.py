#!/usr/bin/env python3
"""
Environment Configuration Setup Script
for Queue Management System

This script helps you create a .env file with proper configuration.
"""

import os
import secrets
import string
from pathlib import Path

def generate_secret_key():
    """Generate a secure secret key"""
    return secrets.token_urlsafe(32)

def generate_password(length=16):
    """Generate a strong password"""
    chars = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(chars) for _ in range(length))

def get_user_input(prompt, default=None, required=True):
    """Get user input with validation"""
    while True:
        if default:
            user_input = input(f"{prompt} (default: {default}): ").strip()
            if not user_input:
                user_input = default
        else:
            user_input = input(f"{prompt}: ").strip()
        
        if user_input or not required:
            return user_input
        print("This field is required. Please enter a value.")

def create_env_file():
    """Create the .env file with user configuration"""
    
    print("🚀 Queue Management System - Environment Configuration")
    print("=" * 60)
    print()
    
    # Check if .env already exists
    env_file = Path(".env")
    if env_file.exists():
        overwrite = input("⚠️  .env file already exists. Overwrite? (y/N): ").strip().lower()
        if overwrite != 'y':
            print("Configuration cancelled.")
            return
    
    print("📋 Please provide the following configuration:")
    print()
    
    # Database Configuration
    print("🗄️  DATABASE CONFIGURATION")
    print("-" * 30)
    
    db_host = get_user_input("Database host", "db")
    db_port = get_user_input("Database port", "5432")
    db_name = get_user_input("Database name", "queue_db")
    db_user = get_user_input("Database username", "queue_user")
    db_password = get_user_input("Database password", "queue_password")
    
    db_url = f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    
    print()
    
    # Admin Configuration
    print("👤 ADMIN CONFIGURATION")
    print("-" * 30)
    
    admin_email = get_user_input("Admin email address", "admin@queue.com")
    admin_password = get_user_input("Admin password", generate_password())
    
    print()
    
    # Security Configuration
    print("🔐 SECURITY CONFIGURATION")
    print("-" * 30)
    
    secret_key = get_user_input("Secret key (JWT)", generate_secret_key())
    
    print()
    
    # SMTP Configuration (Optional)
    print("📧 SMTP CONFIGURATION (Optional - for email alerts)")
    print("-" * 50)
    
    enable_smtp = input("Enable SMTP for email alerts? (y/N): ").strip().lower() == 'y'
    
    smtp_host = ""
    smtp_port = ""
    smtp_user = ""
    smtp_pass = ""
    
    if enable_smtp:
        smtp_host = get_user_input("SMTP host", "smtp.gmail.com")
        smtp_port = get_user_input("SMTP port", "587")
        smtp_user = get_user_input("SMTP username/email")
        smtp_pass = get_user_input("SMTP password/app password")
    
    print()
    
    # Webhook Configuration (Optional)
    print("🔗 WEBHOOK CONFIGURATION (Optional - for Slack/Teams alerts)")
    print("-" * 55)
    
    enable_webhook = input("Enable webhook for Slack/Teams alerts? (y/N): ").strip().lower() == 'y'
    
    webhook_url = ""
    if enable_webhook:
        webhook_url = get_user_input("Webhook URL")
    
    print()
    
    # Queue Configuration
    print("📊 QUEUE CONFIGURATION")
    print("-" * 30)
    
    queue_threshold = get_user_input("Queue length alert threshold", "100")
    
    print()

    # Redis Configuration
    print("🟢 REDIS CONFIGURATION")
    print("-" * 30)
    redis_host = get_user_input("Redis host", "redis")
    redis_port = get_user_input("Redis port", "6379")
    redis_db = get_user_input("Redis database number", "0")
    redis_url = f"redis://{redis_host}:{redis_port}/{redis_db}"
    print()
    
    # Generate .env content
    env_content = f"""# Queue Management System Environment Configuration
# Generated on: {os.popen('date').read().strip()}

# Database Configuration
DB_URL={db_url}

# Redis Configuration
REDIS_URL={redis_url}

# Prometheus Configuration
PROMETHEUS_MULTIPROC_DIR=/tmp

# Admin Configuration
ADMIN_EMAIL={admin_email}
ADMIN_PASSWORD={admin_password}

# Security Configuration
SECRET_KEY={secret_key}

# Queue Configuration
QUEUE_THRESHOLD={queue_threshold}

# SMTP Configuration (for email alerts)
SMTP_HOST={smtp_host}
SMTP_PORT={smtp_port}
SMTP_USER={smtp_user}
SMTP_PASS={smtp_pass}

# Webhook Configuration (for Slack/Teams alerts)
WEBHOOK_URL={webhook_url}

# Optional: Logging Level
# LOG_LEVEL=INFO

# Optional: API Rate Limiting
# RATE_LIMIT_PER_MINUTE=1000
"""
    
    # Write .env file
    try:
        with open(env_file, 'w') as f:
            f.write(env_content)
        
        print("✅ Configuration saved successfully!")
        print(f"📁 File created: {env_file.absolute()}")
        print()
        
        # Show next steps
        print("🚀 Next Steps:")
        print("1. Review the configuration in .env file")
        print("2. Update any values if needed")
        print("3. Start the system: docker-compose up -d")
        print("4. Access the API: http://localhost:8000")
        print("5. View documentation: http://localhost:8000/docs")
        print()
        
        # Show important notes
        print("⚠️  Important Notes:")
        print("- Keep your .env file secure and never commit it to version control")
        print("- Change default passwords in production")
        print("- Use strong, unique passwords for all services")
        print("- Enable 2FA for email accounts used for SMTP")
        print("- Test email and webhook configurations before production use")
        
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")
        return False
    
    return True

def validate_env_file():
    """Validate the created .env file"""
    env_file = Path(".env")
    
    if not env_file.exists():
        print("❌ .env file not found!")
        return False
    
    print("\n🔍 Validating .env file...")
    
    # Load and check environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    required_vars = ['DB_URL', 'SECRET_KEY', 'ADMIN_EMAIL']
    optional_vars = ['SMTP_HOST', 'WEBHOOK_URL']
    
    all_good = True
    
    print("\nRequired variables:")
    for var in required_vars:
        value = os.getenv(var)
        status = "✅" if value else "❌"
        print(f"  {status} {var}: {'Set' if value else 'Missing'}")
        if not value:
            all_good = False
    
    print("\nOptional variables:")
    for var in optional_vars:
        value = os.getenv(var)
        status = "✅" if value else "⚠️"
        print(f"  {status} {var}: {'Set' if value else 'Not configured'}")
    
    if all_good:
        print("\n✅ All required variables are configured!")
    else:
        print("\n❌ Some required variables are missing. Please check your .env file.")
    
    return all_good

if __name__ == "__main__":
    try:
        print("Queue Management System - Environment Setup")
        print("=" * 50)
        print()
        
        # Create .env file
        if create_env_file():
            # Validate the file
            validate_env_file()
        
    except KeyboardInterrupt:
        print("\n\n❌ Configuration cancelled by user.")
    except Exception as e:
        print(f"\n❌ Error during configuration: {e}")
        print("Please check the CONFIGURATION_GUIDE.md for manual setup instructions.") 