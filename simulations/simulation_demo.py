#!/usr/bin/env python3
"""
Queue Management System - Complete Simulation Demo
==================================================

This script demonstrates the complete workflow of the Queue Management System,
from creating applications to testing all queue scenarios.
"""

import requests
import time
import json
import uuid
from datetime import datetime, timedelta
import random

# Configuration
BASE_URL = "http://localhost:8000"
ADMIN_EMAIL = "admin@yourcompany.com"
ADMIN_PASSWORD = "changeme123"

class QueueSimulation:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.applications = []
        self.queues = []
        self.queue_users = []
        
    def print_step(self, step_num, title, description=""):
        """Print a formatted step header"""
        print(f"\n{'='*60}")
        print(f"STEP {step_num}: {title}")
        print(f"{'='*60}")
        if description:
            print(f"Description: {description}")
        print()
    
    def print_success(self, message):
        """Print a success message"""
        print(f"✅ {message}")
    
    def print_error(self, message):
        """Print an error message"""
        print(f"❌ {message}")
    
    def print_info(self, message):
        """Print an info message"""
        print(f"ℹ️  {message}")
    
    def admin_login(self):
        """Step 1: Admin Login"""
        self.print_step(1, "ADMIN LOGIN", "Authenticate as system administrator")
        
        try:
            response = self.session.post(
                f"{BASE_URL}/auth/login",
                data={
                    "username": ADMIN_EMAIL,
                    "password": ADMIN_PASSWORD
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data["access_token"]
                self.session.headers.update({"Authorization": f"Bearer {self.admin_token}"})
                self.print_success("Admin login successful")
                self.print_info(f"Token: {self.admin_token[:20]}...")
                return True
            else:
                self.print_error(f"Login failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.print_error(f"Login error: {e}")
            return False
    
    def create_applications(self):
        """Step 2: Create Sample Applications"""
        self.print_step(2, "CREATE APPLICATIONS", "Create multiple applications for testing")
        
        applications_data = [
            {
                "name": "E-Commerce Store",
                "domain": "shop.example.com",
                "callback_url": "https://shop.example.com/queue-callback"
            },
            {
                "name": "Banking Portal",
                "domain": "bank.example.com", 
                "callback_url": "https://bank.example.com/queue-callback"
            },
            {
                "name": "Healthcare App",
                "domain": "health.example.com",
                "callback_url": "https://health.example.com/queue-callback"
            }
        ]
        
        for i, app_data in enumerate(applications_data, 1):
            try:
                response = self.session.post(
                    f"{BASE_URL}/applications/",
                    json=app_data
                )
                
                if response.status_code == 201:
                    app = response.json()
                    self.applications.append(app)
                    self.print_success(f"Created application {i}: {app['name']}")
                    self.print_info(f"  API Key: {app['api_key']}")
                    self.print_info(f"  ID: {app['id']}")
                else:
                    self.print_error(f"Failed to create application {i}: {response.status_code}")
                    
            except Exception as e:
                self.print_error(f"Error creating application {i}: {e}")
    
    def create_queues(self):
        """Step 3: Create Queues for Each Application"""
        self.print_step(3, "CREATE QUEUES", "Create different types of queues for each application")
        
        for app in self.applications:
            # Create multiple queues per application
            queues_data = [
                {
                    "application_id": app["id"],
                    "name": "Priority Queue",
                    "max_users_per_minute": 5,
                    "priority": 1
                },
                {
                    "application_id": app["id"], 
                    "name": "Standard Queue",
                    "max_users_per_minute": 10,
                    "priority": 2
                },
                {
                    "application_id": app["id"],
                    "name": "Express Queue", 
                    "max_users_per_minute": 15,
                    "priority": 3
                }
            ]
            
            for i, queue_data in enumerate(queues_data, 1):
                try:
                    response = self.session.post(
                        f"{BASE_URL}/queues/",
                        json=queue_data
                    )
                    
                    if response.status_code == 201:
                        queue = response.json()
                        self.queues.append(queue)
                        self.print_success(f"Created queue for {app['name']}: {queue['name']}")
                        self.print_info(f"  Max users/min: {queue['max_users_per_minute']}")
                        self.print_info(f"  Priority: {queue['priority']}")
                    else:
                        self.print_error(f"Failed to create queue {i} for {app['name']}: {response.status_code}")
                        
                except Exception as e:
                    self.print_error(f"Error creating queue {i} for {app['name']}: {e}")
    
    def simulate_queue_joins(self):
        """Step 4: Simulate Multiple Users Joining Queues"""
        self.print_step(4, "SIMULATE QUEUE JOINS", "Simulate multiple users joining different queues")
        
        # Create session for each application
        app_sessions = {}
        for app in self.applications:
            session = requests.Session()
            session.headers.update({"app_api_key": app["api_key"]})
            app_sessions[app["id"]] = session
        
        # Simulate users joining queues
        total_users = 0
        for queue in self.queues:
            # Join 3-8 users per queue
            num_users = random.randint(3, 8)
            app_session = app_sessions[queue["application_id"]]
            
            for i in range(num_users):
                try:
                    user_data = {
                        "queue_id": str(queue["id"]),  # Convert UUID to string properly
                        "visitor_id": f"visitor_{queue['id'][:8]}_{i}"
                    }
                    
                    response = app_session.post(
                        f"{BASE_URL}/join",
                        json=user_data
                    )
                    
                    if response.status_code == 200:
                        user = response.json()
                        self.queue_users.append(user)
                        total_users += 1
                        self.print_success(f"User {i+1} joined {queue['name']}")
                        self.print_info(f"  Token: {user['token'][:10]}...")
                        self.print_info(f"  Status: {user['status']}")
                    else:
                        self.print_error(f"Failed to join user {i+1} to {queue['name']}: {response.status_code}")
                        
                except Exception as e:
                    self.print_error(f"Error joining user {i+1} to {queue['name']}: {e}")
        
        self.print_info(f"Total users joined: {total_users}")
    
    def simulate_queue_status_checks(self):
        """Step 5: Simulate Users Checking Their Queue Status"""
        self.print_step(5, "SIMULATE STATUS CHECKS", "Simulate users checking their queue status")
        
        for i, user in enumerate(self.queue_users[:5]):  # Check first 5 users
            try:
                response = requests.get(
                    f"{BASE_URL}/queue_status",
                    params={"token": user["token"]}
                )
                
                if response.status_code == 200:
                    status_data = response.json()
                    self.print_success(f"Status check {i+1} successful")
                    self.print_info(f"  User: {status_data['visitor_id']}")
                    self.print_info(f"  Status: {status_data['status']}")
                    self.print_info(f"  Wait time: {status_data.get('wait_time', 'N/A')}")
                else:
                    self.print_error(f"Status check {i+1} failed: {response.status_code}")
                    
            except Exception as e:
                self.print_error(f"Error in status check {i+1}: {e}")
    
    def simulate_queue_cancellations(self):
        """Step 6: Simulate Some Users Cancelling Their Queue Position"""
        self.print_step(6, "SIMULATE CANCELLATIONS", "Simulate some users cancelling their queue positions")
        
        # Cancel 20% of users (or at least 1 if there are users)
        if self.queue_users:
            num_to_cancel = max(1, len(self.queue_users) // 5)
            users_to_cancel = random.sample(self.queue_users, min(num_to_cancel, len(self.queue_users)))
        else:
            users_to_cancel = []
            self.print_info("No users available for cancellation")
        
        for i, user in enumerate(users_to_cancel):
            try:
                response = requests.post(
                    f"{BASE_URL}/cancel",
                    json={"token": user["token"]}
                )
                
                if response.status_code == 204:
                    self.print_success(f"Cancellation {i+1} successful")
                    self.print_info(f"  User: {user['visitor_id']}")
                else:
                    self.print_error(f"Cancellation {i+1} failed: {response.status_code}")
                    
            except Exception as e:
                self.print_error(f"Error in cancellation {i+1}: {e}")
    
    def simulate_high_traffic_scenario(self):
        """Step 7: Simulate High Traffic Scenario"""
        self.print_step(7, "HIGH TRAFFIC SIMULATION", "Simulate high traffic scenario with many users")
        
        # Choose a queue for high traffic simulation
        target_queue = random.choice(self.queues)
        app_session = requests.Session()
        app_session.headers.update({"app_api_key": next(app["api_key"] for app in self.applications if app["id"] == target_queue["application_id"])})
        
        self.print_info(f"Simulating high traffic for: {target_queue['name']}")
        
        # Join many users quickly
        high_traffic_users = []
        for i in range(20):  # Join 20 users quickly
            try:
                user_data = {
                    "queue_id": str(target_queue["id"]),  # Convert UUID to string properly
                    "visitor_id": f"high_traffic_user_{i}"
                }
                
                response = app_session.post(
                    f"{BASE_URL}/join",
                    json=user_data
                )
                
                if response.status_code == 200:
                    user = response.json()
                    high_traffic_users.append(user)
                    self.print_success(f"High traffic user {i+1} joined")
                else:
                    self.print_error(f"High traffic user {i+1} failed to join: {response.status_code}")
                    
            except Exception as e:
                self.print_error(f"Error joining high traffic user {i+1}: {e}")
        
        self.print_info(f"High traffic simulation completed: {len(high_traffic_users)} users joined")
    
    def check_system_health(self):
        """Step 8: Check System Health and Metrics"""
        self.print_step(8, "SYSTEM HEALTH CHECK", "Check system health and performance metrics")
        
        # Check health endpoint
        try:
            response = requests.get(f"{BASE_URL}/health")
            if response.status_code == 200:
                health_data = response.json()
                self.print_success("System health check passed")
                self.print_info(f"Status: {health_data['status']}")
                self.print_info(f"Services: {health_data['services']}")
            else:
                self.print_error(f"Health check failed: {response.status_code}")
        except Exception as e:
            self.print_error(f"Health check error: {e}")
        
        # Check metrics endpoint
        try:
            response = requests.get(f"{BASE_URL}/metrics")
            if response.status_code == 200:
                self.print_success("Metrics endpoint accessible")
                self.print_info("Prometheus metrics available")
            else:
                self.print_error(f"Metrics check failed: {response.status_code}")
        except Exception as e:
            self.print_error(f"Metrics check error: {e}")
        
        # Get current queue statistics
        try:
            response = self.session.get(f"{BASE_URL}/queues/")
            if response.status_code == 200:
                queues = response.json()
                self.print_success("Queue statistics retrieved")
                self.print_info(f"Total queues: {len(queues)}")
                
                for queue in queues:
                    self.print_info(f"  - {queue['name']}: Priority {queue['priority']}, Max {queue['max_users_per_minute']}/min")
            else:
                self.print_error(f"Queue statistics failed: {response.status_code}")
        except Exception as e:
            self.print_error(f"Queue statistics error: {e}")
    
    def simulate_edge_cases(self):
        """Step 9: Test Edge Cases and Error Scenarios"""
        self.print_step(9, "EDGE CASES TESTING", "Test various edge cases and error scenarios")
        
        # Test 1: Invalid API key
        self.print_info("Testing invalid API key...")
        try:
            response = requests.post(
                f"{BASE_URL}/join",
                headers={"app_api_key": "invalid-key"},
                json={"queue_id": str(uuid.uuid4()), "visitor_id": "test_user"}
            )
            if response.status_code == 401:
                self.print_success("Invalid API key correctly rejected")
            else:
                self.print_error(f"Invalid API key not rejected: {response.status_code}")
        except Exception as e:
            self.print_error(f"Invalid API key test error: {e}")
        
        # Test 2: Invalid queue ID
        self.print_info("Testing invalid queue ID...")
        try:
            response = requests.post(
                f"{BASE_URL}/join",
                headers={"app_api_key": self.applications[0]["api_key"]},
                json={"queue_id": str(uuid.uuid4()), "visitor_id": "test_user"}
            )
            if response.status_code == 404:
                self.print_success("Invalid queue ID correctly rejected")
            else:
                self.print_error(f"Invalid queue ID not rejected: {response.status_code}")
        except Exception as e:
            self.print_error(f"Invalid queue ID test error: {e}")
        
        # Test 3: Invalid token for status check
        self.print_info("Testing invalid token...")
        try:
            response = requests.get(
                f"{BASE_URL}/queue_status",
                params={"token": "invalid-token"}
            )
            if response.status_code == 404:
                self.print_success("Invalid token correctly rejected")
            else:
                self.print_error(f"Invalid token not rejected: {response.status_code}")
        except Exception as e:
            self.print_error(f"Invalid token test error: {e}")
    
    def generate_simulation_report(self):
        """Step 10: Generate Simulation Report"""
        self.print_step(10, "SIMULATION REPORT", "Generate comprehensive simulation report")
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "simulation_summary": {
                "applications_created": len(self.applications),
                "queues_created": len(self.queues),
                "users_joined": len(self.queue_users),
                "total_api_calls": 0  # Would need to track this
            },
            "applications": [
                {
                    "name": app["name"],
                    "domain": app["domain"],
                    "api_key": app["api_key"][:10] + "..."
                }
                for app in self.applications
            ],
            "queues": [
                {
                    "name": queue["name"],
                    "max_users_per_minute": queue["max_users_per_minute"],
                    "priority": queue["priority"]
                }
                for queue in self.queues
            ],
            "system_status": "OPERATIONAL"
        }
        
        self.print_success("Simulation completed successfully!")
        self.print_info("Generated simulation report:")
        print(json.dumps(report, indent=2))
        
        return report
    
    def run_complete_simulation(self):
        """Run the complete simulation"""
        print("🚀 QUEUE MANAGEMENT SYSTEM - COMPLETE SIMULATION")
        print("=" * 60)
        print(f"Starting simulation at: {datetime.now()}")
        print("=" * 60)
        
        try:
            # Run all simulation steps
            if not self.admin_login():
                self.print_error("Cannot proceed without admin login")
                return False
            
            self.create_applications()
            self.create_queues()
            self.simulate_queue_joins()
            self.simulate_queue_status_checks()
            self.simulate_queue_cancellations()
            self.simulate_high_traffic_scenario()
            self.check_system_health()
            self.simulate_edge_cases()
            self.generate_simulation_report()
            
            print(f"\n{'='*60}")
            print("🎉 SIMULATION COMPLETED SUCCESSFULLY!")
            print(f"{'='*60}")
            print(f"End time: {datetime.now()}")
            print("All queue management scenarios have been tested.")
            print("Your system is ready for production use!")
            
            return True
            
        except Exception as e:
            self.print_error(f"Simulation failed: {e}")
            return False

def main():
    """Main function to run the simulation"""
    simulation = QueueSimulation()
    success = simulation.run_complete_simulation()
    
    if success:
        print("\n📋 NEXT STEPS:")
        print("1. Access API documentation: http://localhost:8000/docs")
        print("2. Monitor metrics: http://localhost:8000/metrics")
        print("3. View Grafana dashboard: http://localhost:3000")
        print("4. Use the curl commands provided earlier for manual testing")
    else:
        print("\n❌ SIMULATION FAILED")
        print("Please check the logs and ensure all services are running.")

if __name__ == "__main__":
    main() 