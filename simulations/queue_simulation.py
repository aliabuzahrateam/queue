#!/usr/bin/env python3
"""
Queue Management System - 10 Minute Real Simulation
This script simulates a real queue system with:
- Adding users for 10 minutes
- Processing users (waiting -> ready)
- Handling user expiration
- Real-time flow monitoring
"""

import requests
import time
import json
from datetime import datetime, timedelta
import uuid
from typing import List, Dict, Any
import threading
from dataclasses import dataclass
from collections import defaultdict
import os
import random

# Configuration
BASE_URL = "http://localhost:8000"
API_KEY = "sample-api-key-123"  # Use existing API key from database
SIMULATION_DURATION_MINUTES = 10
REPORT_INTERVAL_SECONDS = 60  # Report every minute
USERS_PER_MINUTE = 15  # More than max_users_per_minute (10)
MAX_USERS_PER_MINUTE = 10
PROCESSING_RATE_PER_MINUTE = 8  # Users processed per minute
USER_EXPIRY_MINUTES = 10  # Users expire after 10 minutes

@dataclass
class UserReport:
    visitor_id: str
    created_at: datetime
    expires_at: datetime
    estimated_waiting_time: int
    wait_time: int
    status: str
    position_in_queue: int

class QueueSimulation:
    def __init__(self):
        self.base_url = BASE_URL
        self.api_key = API_KEY
        self.application_id = None
        self.queue_id = None
        self.users_joined = []
        self.reports = []
        self.simulation_start_time = None
        self.simulation_end_time = None
        self.reporting_active = True
        self.processing_active = True
        self.user_tokens = {}  # Track tokens for processing
        
    def setup_application_and_queue(self):
        """Use existing application and queue for simulation"""
        print("🔧 Setting up application and queue...")
        
        # Get existing application
        response = requests.get(f"{self.base_url}/applications/")
        if response.status_code == 200:
            applications = response.json()
            if applications:
                # Use the first application
                app = applications[0]
                self.application_id = app["id"]
                print(f"✅ Using existing application: {self.application_id} ({app['name']})")
            else:
                print("❌ No applications found in database")
                return False
        else:
            print(f"❌ Failed to get applications: {response.text}")
            return False
            
        # Get existing queue for this application
        response = requests.get(f"{self.base_url}/queues/")
        if response.status_code == 200:
            queues = response.json()
            app_queues = [q for q in queues if q["application_id"] == self.application_id]
            if app_queues:
                # Use the first queue for this application
                queue = app_queues[0]
                self.queue_id = queue["id"]
                print(f"✅ Using existing queue: {self.queue_id} ({queue['name']})")
            else:
                print("❌ No queues found for this application")
                return False
        else:
            print(f"❌ Failed to get queues: {response.text}")
            return False
            
        return True
    
    def join_queue(self, visitor_id: str) -> Dict[str, Any]:
        """Join a user to the queue"""
        headers = {"app_api_key": self.api_key}
        data = {
            "queue_id": self.queue_id,
            "visitor_id": visitor_id
        }
        
        response = requests.post(f"{self.base_url}/join", json=data, headers=headers)
        if response.status_code == 201:
            return response.json()
        else:
            print(f"❌ Failed to join queue for {visitor_id}: {response.text}")
            return None
    
    def get_queue_status(self, token: str) -> Dict[str, Any]:
        """Get status of a user in the queue"""
        response = requests.get(f"{self.base_url}/queue_status?token={token}")
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Failed to get queue status for token {token}: {response.text}")
            return None
    
    def process_user(self, token: str) -> bool:
        """Process a user (move from waiting to ready) - simulate by updating status"""
        # In a real system, this would be done by the queue worker
        # For simulation, we'll just track the status change
        return True
    
    def expire_user(self, token: str) -> bool:
        """Expire a user (move from waiting to expired)"""
        # In a real system, this would be done by the queue worker
        # For simulation, we'll just track the status change
        return True
    
    def calculate_estimated_wait_time(self, position: int) -> int:
        """Calculate estimated wait time based on position in queue"""
        # Assume each user takes 1 minute to process
        return position * 60
    
    def calculate_actual_wait_time(self, created_at: datetime) -> int:
        """Calculate actual wait time since joining"""
        return int((datetime.utcnow() - created_at).total_seconds())
    
    def generate_minute_report(self, minute_number: int):
        """Generate a comprehensive report for the current minute"""
        print(f"\n📊 MINUTE {minute_number} REPORT - {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        # Get current queue status for all users
        active_users = []
        inflow_users = []
        outflow_users = []
        waiting_users = []
        ready_users = []
        expired_users = []
        est_wait_times = []
        now = datetime.utcnow()
        minute_start = self.simulation_start_time + timedelta(minutes=minute_number-1)
        minute_end = minute_start + timedelta(minutes=1)
        
        for user in self.users_joined:
            if user.get('token'):
                status = self.get_queue_status(user['token'])
                if status:
                    created_at = user['created_at']
                    # Inflow: joined in this minute
                    if minute_start <= created_at < minute_end:
                        inflow_users.append(user['visitor_id'])
                    
                    # Update user status
                    user['status'] = status['status']
                    
                    # Categorize users by status
                    if status['status'] == 'waiting':
                        waiting_users.append(user['visitor_id'])
                        # Estimate wait time
                        position = len([u for u in self.users_joined if u['created_at'] <= created_at and u.get('status') == 'waiting'])
                        est_wait = self.calculate_estimated_wait_time(position)
                        est_wait_times.append(est_wait)
                    elif status['status'] == 'ready':
                        ready_users.append(user['visitor_id'])
                        # Check if just became ready in this minute
                        if 'last_status' in user and user['last_status'] == 'waiting':
                            if minute_start <= now < minute_end:
                                outflow_users.append(user['visitor_id'])
                    elif status['status'] == 'expired':
                        expired_users.append(user['visitor_id'])
                        # Check if just expired in this minute
                        if 'last_status' in user and user['last_status'] == 'waiting':
                            if minute_start <= now < minute_end:
                                outflow_users.append(user['visitor_id'])
                    
                    # Track last status for next report
                    user['last_status'] = status['status']
        
        inflow = len(inflow_users)
        queue = len(waiting_users)
        outflow = len(outflow_users)
        inflow_queue_ratio = inflow / queue if queue else 0
        avg_est_wait = sum(est_wait_times) // len(est_wait_times) if est_wait_times else 0
        
        print(f"Inflow: {inflow}")
        print(f"Queue: {queue}")
        print(f"Outflow: {outflow}")
        print(f"Inflow/Queue: {inflow_queue_ratio:.2f}")
        print(f"Avg Estimated Waiting Time: {avg_est_wait//60}m {avg_est_wait%60}s")
        print(f"Ready Users: {len(ready_users)}")
        print(f"Expired Users: {len(expired_users)}")
        print("-" * 80)
        
        # Store summary in report
        self.reports.append({
            'minute': minute_number,
            'timestamp': now.isoformat(),
            'inflow': inflow,
            'queue': queue,
            'outflow': outflow,
            'inflow_queue_ratio': inflow_queue_ratio,
            'avg_estimated_waiting_time': avg_est_wait,
            'ready_users': len(ready_users),
            'expired_users': len(expired_users),
            'inflow_users': inflow_users,
            'waiting_users': waiting_users,
            'outflow_users': outflow_users
        })
    
    def add_users_for_minute(self, minute_number: int):
        """Add users for a specific minute"""
        print(f"\n👥 Adding users for minute {minute_number}...")
        
        for i in range(USERS_PER_MINUTE):
            visitor_id = f"visitor_{minute_number:02d}_{i:02d}"
            user_data = self.join_queue(visitor_id)
            
            if user_data:
                self.users_joined.append({
                    'visitor_id': visitor_id,
                    'token': user_data.get('token'),
                    'created_at': datetime.utcnow(),
                    'status': user_data.get('status', 'waiting')
                })
                self.user_tokens[visitor_id] = user_data.get('token')
                print(f"   ✅ {visitor_id} joined queue")
            else:
                print(f"   ❌ Failed to add {visitor_id}")
            
            # Small delay between users
            time.sleep(0.1)
    
    def process_queue_worker(self):
        """Background worker that processes users in the queue"""
        print("🔄 Starting queue processing worker...")
        
        while self.processing_active:
            try:
                # Get all waiting users
                waiting_users = [u for u in self.users_joined if u.get('status') == 'waiting']
                
                if waiting_users:
                    # Process users at the processing rate
                    users_to_process = min(PROCESSING_RATE_PER_MINUTE // 60, len(waiting_users))
                    
                    for i in range(users_to_process):
                        if i < len(waiting_users):
                            user = waiting_users[i]
                            if self.process_user(user['token']):
                                user['status'] = 'ready'
                                print(f"   🔄 Processed {user['visitor_id']} (waiting -> ready)")
                
                # Check for expired users
                now = datetime.utcnow()
                for user in self.users_joined:
                    if user.get('status') == 'waiting':
                        created_at = user['created_at']
                        if (now - created_at).total_seconds() > USER_EXPIRY_MINUTES * 60:
                            if self.expire_user(user['token']):
                                user['status'] = 'expired'
                                print(f"   ⏰ Expired {user['visitor_id']} (waiting -> expired)")
                
                time.sleep(1)  # Process every second
                
            except Exception as e:
                print(f"❌ Error in queue worker: {e}")
                time.sleep(1)
    
    def reporting_thread(self):
        """Thread for generating reports every minute"""
        minute_counter = 1
        
        while self.reporting_active:
            time.sleep(REPORT_INTERVAL_SECONDS)
            if self.reporting_active:
                self.generate_minute_report(minute_counter)
                minute_counter += 1
    
    def run_simulation(self):
        """Run the complete simulation"""
        print("🚀 Starting 10-Minute Real Queue Simulation")
        print("=" * 50)
        
        # Setup
        if not self.setup_application_and_queue():
            print("❌ Failed to setup application and queue")
            return
        
        self.simulation_start_time = datetime.utcnow()
        print(f"⏰ Simulation started at: {self.simulation_start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Start processing worker thread
        worker_thread = threading.Thread(target=self.process_queue_worker)
        worker_thread.start()
        
        # Start reporting thread
        report_thread = threading.Thread(target=self.reporting_thread)
        report_thread.start()
        
        # Add users for 10 minutes
        for minute in range(1, SIMULATION_DURATION_MINUTES + 1):
            print(f"\n🕐 Minute {minute}/{SIMULATION_DURATION_MINUTES}")
            self.add_users_for_minute(minute)
            
            # Wait until next minute (accounting for time spent adding users)
            elapsed = (datetime.utcnow() - self.simulation_start_time).total_seconds()
            time_to_wait = max(0, 60 - (elapsed % 60))
            if time_to_wait > 0:
                print(f"⏳ Waiting {time_to_wait:.1f} seconds until next minute...")
                time.sleep(time_to_wait)
        
        # Stop adding users
        print(f"\n🛑 Stopped adding users after {SIMULATION_DURATION_MINUTES} minutes")
        print(f"📊 Total users added: {len(self.users_joined)}")
        
        # Continue processing and reporting for a few more minutes
        print(f"\n📈 Continuing to process queue for 5 more minutes...")
        time.sleep(5 * 60)  # Monitor for 5 more minutes
        
        # Stop all threads
        self.reporting_active = False
        self.processing_active = False
        report_thread.join()
        worker_thread.join()
        
        # Final report
        self.simulation_end_time = datetime.utcnow()
        print(f"\n🏁 Simulation completed at: {self.simulation_end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Save detailed report to file
        self.save_final_report()
    
    def save_final_report(self):
        """Save the complete simulation report to a file"""
        report_data = {
            'simulation_info': {
                'start_time': self.simulation_start_time.isoformat(),
                'end_time': self.simulation_end_time.isoformat(),
                'duration_minutes': SIMULATION_DURATION_MINUTES,
                'users_per_minute': USERS_PER_MINUTE,
                'max_users_per_minute': MAX_USERS_PER_MINUTE,
                'processing_rate_per_minute': PROCESSING_RATE_PER_MINUTE,
                'user_expiry_minutes': USER_EXPIRY_MINUTES,
                'total_users_added': len(self.users_joined)
            },
            'application_id': self.application_id,
            'queue_id': self.queue_id,
            'minute_reports': self.reports
        }
        
        filename = f"queue_simulation_report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(report_data, f, indent=2, default=str)
        
        print(f"📄 Detailed report saved to: {filename}")
        
        # Print summary
        print(f"\n📋 SIMULATION SUMMARY:")
        print(f"   Duration: {SIMULATION_DURATION_MINUTES} minutes")
        print(f"   Users per minute: {USERS_PER_MINUTE}")
        print(f"   Processing rate: {PROCESSING_RATE_PER_MINUTE} users/minute")
        print(f"   User expiry: {USER_EXPIRY_MINUTES} minutes")
        print(f"   Total users added: {len(self.users_joined)}")
        print(f"   Reports generated: {len(self.reports)}")
        print(f"   Report file: {filename}")

REPORTS_DIR = os.path.join(os.path.dirname(__file__), "reports")
os.makedirs(REPORTS_DIR, exist_ok=True)

class MultiAppQueueSimulation:
    def __init__(self):
        self.base_url = BASE_URL
        self.api_key = API_KEY
        self.applications = []  # List of dicts: {id, name, queues: [queue dicts]}
        self.reports = []

    def create_applications_and_queues(self, num_apps=3, queues_per_app=3):
        print(f"Creating {num_apps} applications, each with {queues_per_app} queues...")
        for app_idx in range(num_apps):
            app_data = {
                "name": f"SimApp_{app_idx+1}",
                "domain": f"simapp{app_idx+1}.example.com",
                "callback_url": f"https://simapp{app_idx+1}.example.com/webhook"
            }
            resp = requests.post(f"{self.base_url}/applications/", json=app_data)
            if resp.status_code == 201:
                app = resp.json()
                app_entry = {"id": app["id"], "name": app["name"], "api_key": app["api_key"], "queues": []}
                print(f"  ✅ Created application: {app['name']} ({app['id']}) with API key: {app['api_key']}")
                for q_idx in range(queues_per_app):
                    queue_data = {
                        "application_id": app["id"],
                        "name": f"Queue_{q_idx+1}_of_{app['name']}",
                        "max_users_per_minute": random.randint(8, 15),
                        "priority": 1
                    }
                    q_resp = requests.post(f"{self.base_url}/queues/", json=queue_data)
                    if q_resp.status_code == 201:
                        queue = q_resp.json()
                        app_entry["queues"].append(queue)
                        print(f"    ✅ Created queue: {queue['name']} (max {queue['max_users_per_minute']}/min)")
                    else:
                        print(f"    ❌ Failed to create queue: {q_resp.text}")
                self.applications.append(app_entry)
            else:
                print(f"  ❌ Failed to create application: {resp.text}")

    def run_crowding_simulation(self, app, queue, scenario, minutes=5):
        """Run a crowding simulation for a queue and save the report."""
        print(f"\n=== {scenario.upper()} CROWDING: {app['name']} / {queue['name']} ===")
        max_users = queue['max_users_per_minute']
        users_joined = []
        reports = []
        minute = 0
        waiting = True
        user_counter = 0
        simulation_start = datetime.utcnow()
        # Use the correct API key for this application
        app_api_key = app.get('api_key', API_KEY)
        while waiting:
            inflow = 0
            if minute < minutes:
                if scenario == 'low':
                    users_this_minute = random.randint(1, max_users-1)
                elif scenario == 'medium':
                    if random.random() < 0.5:
                        users_this_minute = random.randint(1, max_users-1)
                    else:
                        users_this_minute = random.randint(max_users, max_users+5)
                elif scenario == 'high':
                    users_this_minute = random.randint(max_users+1, max_users+10)
                else:
                    users_this_minute = 1
                for i in range(users_this_minute):
                    visitor_id = f"{scenario}_app{app['name']}_q{queue['name']}_m{minute+1}_u{user_counter}"
                    headers = {"app_api_key": app_api_key}
                    data = {"queue_id": queue['id'], "visitor_id": visitor_id}
                    resp = requests.post(f"{self.base_url}/join", json=data, headers=headers)
                    print(f"  DEBUG: Join attempt for {visitor_id} - Status: {resp.status_code}, Response: {resp.text}")
                    if resp.status_code == 201:
                        users_joined.append({
                            'visitor_id': visitor_id,
                            'token': resp.json().get('token'),
                            'created_at': datetime.utcnow(),
                            'status': resp.json().get('status', 'waiting')
                        })
                        inflow += 1
                    else:
                        print(f"  ERROR: Failed to join {visitor_id} - {resp.status_code}: {resp.text}")
                    user_counter += 1
            # Wait 1 minute (simulate minute passing)
            time.sleep(0.1)  # Use 0.1s for speed; change to 60 for real time
            # Check queue status
            waiting_users = 0
            for user in users_joined:
                if user.get('token'):
                    status = requests.get(f"{self.base_url}/queue_status?token={user['token']}")
                    if status.status_code == 200 and status.json()['status'] == 'waiting':
                        waiting_users += 1
            # Generate report for this minute
            report = {
                'minute': minute+1,
                'inflow': inflow,
                'queue_waiting': waiting_users,
                'total_joined': len(users_joined),
                'timestamp': (simulation_start + timedelta(minutes=minute)).isoformat()
            }
            reports.append(report)
            print(f"Minute {minute+1}: Inflow={inflow}, Waiting={waiting_users}, Total={len(users_joined)}")
            minute += 1
            # Continue until no users are waiting
            if minute >= minutes and waiting_users == 0:
                waiting = False
        # Save report
        report_file = os.path.join(REPORTS_DIR, f"{scenario}_{app['name']}_{queue['name']}_report.json")
        with open(report_file, 'w') as f:
            json.dump(reports, f, indent=2)
        print(f"Report saved: {report_file}")

    def run_all_scenarios(self):
        for app in self.applications:
            for queue in app['queues']:
                for scenario in ['low', 'medium', 'high']:
                    self.run_crowding_simulation(app, queue, scenario)

if __name__ == "__main__":
    sim = MultiAppQueueSimulation()
    sim.create_applications_and_queues(num_apps=3, queues_per_app=3)
    sim.run_all_scenarios() 