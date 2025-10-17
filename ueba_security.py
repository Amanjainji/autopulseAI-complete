"""
UEBA (User and Entity Behavior Analytics) Security Layer
Monitors AI agent activities and detects anomalous behavior
"""

from datetime import datetime
from typing import Dict, List
import sqlite3
import random


class UEBAMonitor:
    """User and Entity Behavior Analytics for AI Agent Security"""
    
    def __init__(self):
        self.behaviour_log = []
        self.agent_baselines = {
            "DataAnalysisAgent": {
                "allowed_resources": ["sensor_data", "vehicles", "predictions"],
                "max_actions_per_minute": 20
            },
            "DiagnosisAgent": {
                "allowed_resources": ["predictions", "vehicles", "sensor_data"],
                "max_actions_per_minute": 15
            },
            "CustomerEngagementAgent": {
                "allowed_resources": ["customers", "vehicles", "predictions", "appointments"],
                "max_actions_per_minute": 25
            },
            "SchedulingAgent": {
                "allowed_resources": ["appointments", "vehicles", "customers"],
                "max_actions_per_minute": 30
            },
            "FeedbackAgent": {
                "allowed_resources": ["service_records", "customers", "vehicles"],
                "max_actions_per_minute": 15
            },
            "ManufacturingInsightsAgent": {
                "allowed_resources": ["predictions", "service_records", "manufacturing_feedback"],
                "max_actions_per_minute": 10
            },
            "MasterAgent": {
                "allowed_resources": ["all"],
                "max_actions_per_minute": 50
            }
        }
        self.anomaly_threshold = 0.7
        self.alert_count = 0
        # Ensure audit table exists
        try:
            conn = sqlite3.connect('vehicle_maintenance.db')
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS agent_activity_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    agent_name TEXT,
                    action TEXT,
                    timestamp TEXT,
                    resource_accessed TEXT,
                    is_anomalous INTEGER,
                    anomaly_score REAL
                )
            ''')
            conn.commit()
            conn.close()
        except Exception:
            pass
    
    def log_activity(self, agent_name: str, action: str, resource: str = "") -> bool:
        """
        Log agent activity and check for anomalies
        Returns True if activity is authorized, False if anomalous
        """
        timestamp = datetime.now().isoformat()
        anomaly_score = self._calculate_anomaly_score(agent_name, action, resource)
        is_anomalous = anomaly_score > self.anomaly_threshold
        
        entry = {
            "agent": agent_name,
            "action": action,
            "resource": resource,
            "timestamp": timestamp,
            "is_anomalous": is_anomalous,
            "anomaly_score": anomaly_score
        }
        
        self.behaviour_log.append(entry)
        
        # Keep only last 1000 entries in memory
        if len(self.behaviour_log) > 1000:
            self.behaviour_log = self.behaviour_log[-1000:]
        
        # Store in database for audit trail
        try:
            conn = sqlite3.connect('vehicle_maintenance.db')
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO agent_activity_log 
                (agent_name, action, timestamp, resource_accessed, is_anomalous, anomaly_score)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (agent_name, action, timestamp, resource, int(is_anomalous), anomaly_score))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Warning: Could not log to database: {e}")
        
        if is_anomalous:
            self.alert_count += 1
            self._trigger_alert(agent_name, action, resource, anomaly_score, timestamp)
            return False  # Block anomalous activity
        
        return True  # Allow normal activity
    
    def _calculate_anomaly_score(self, agent_name: str, action: str, resource: str) -> float:
        """
        Calculate anomaly score based on agent behavior baseline
        Returns score between 0.0 (normal) and 1.0 (highly anomalous)
        """
        
        # Unknown agent
        if agent_name not in self.agent_baselines:
            return 0.95
        
        baseline = self.agent_baselines[agent_name]
        score = 0.0
        
        # Check resource access authorization
        allowed_resources = baseline["allowed_resources"]
        if resource and "all" not in allowed_resources:
            if resource not in allowed_resources:
                # Unauthorized resource access
                score += 0.8
        
        # Check for suspicious action keywords
        suspicious_keywords = [
            "unauthorized", "bypass", "override", "delete_all", 
            "drop_table", "admin", "root", "hack"
        ]
        if any(keyword in action.lower() for keyword in suspicious_keywords):
            score += 0.7
        
        # Check activity frequency
        recent_actions = [
            log for log in self.behaviour_log[-100:] 
            if log["agent"] == agent_name and 
            (datetime.now() - datetime.fromisoformat(log["timestamp"])).seconds < 60
        ]
        
        max_actions = baseline.get("max_actions_per_minute", 20)
        if len(recent_actions) > max_actions:
            score += 0.5
        
        # Check for unusual time patterns (e.g., actions at odd hours)
        hour = datetime.now().hour
        if hour < 6 or hour > 22:  # Outside business hours
            score += 0.2
        
        # Add small random variation to simulate ML-based detection
        score += random.uniform(0.0, 0.1)
        
        return min(score, 1.0)
    
    def _trigger_alert(self, agent_name: str, action: str, resource: str, 
                       anomaly_score: float, timestamp: str):
        """Trigger security alert for anomalous behavior"""
        
        alert_msg = f"\n{'='*80}\n"
        alert_msg += "⚠️  UEBA SECURITY ALERT ⚠️\n"
        alert_msg += f"{'='*80}\n"
        alert_msg += f"Alert ID: UEBA-{self.alert_count}\n"
        alert_msg += f"Timestamp: {timestamp}\n"
        alert_msg += f"Agent: {agent_name}\n"
        alert_msg += f"Action: {action}\n"
        alert_msg += f"Resource Accessed: {resource}\n"
        alert_msg += f"Anomaly Score: {anomaly_score:.2f} (Threshold: {self.anomaly_threshold})\n"
        alert_msg += f"\n🔒 ACTION TAKEN: Activity blocked and logged\n"
        alert_msg += f"{'='*80}\n"
        
        print(alert_msg)
        
        # In production environment, this would:
        # 1. Send alert to security team via email/SMS
        # 2. Log to SIEM system
        # 3. Temporarily suspend agent if multiple violations
        # 4. Trigger incident response workflow
    
    def get_anomaly_report(self) -> List[Dict]:
        """Get all anomalous activities detected"""
        return [log for log in self.behaviour_log if log["is_anomalous"]]
    
    def get_agent_statistics(self, agent_name: str) -> Dict:
        """Get activity statistics for specific agent"""
        agent_logs = [log for log in self.behaviour_log if log["agent"] == agent_name]
        
        if not agent_logs:
            return {"agent": agent_name, "total_actions": 0, "anomalies": 0}
        
        total_actions = len(agent_logs)
        anomalies = len([log for log in agent_logs if log["is_anomalous"]])
        
        return {
            "agent": agent_name,
            "total_actions": total_actions,
            "anomalies": anomalies,
            "anomaly_rate": f"{(anomalies/total_actions)*100:.2f}%",
            "most_common_action": self._most_common([log["action"] for log in agent_logs]),
            "most_accessed_resource": self._most_common([log["resource"] for log in agent_logs if log["resource"]])
        }
    
    def _most_common(self, items: List[str]) -> str:
        """Find most common item in list"""
        if not items:
            return "N/A"
        return max(set(items), key=items.count)
    
    def generate_security_report(self) -> str:
        """Generate comprehensive security report"""
        report = "\n" + "="*80 + "\n"
        report += "🔐 UEBA SECURITY REPORT\n"
        report += "="*80 + "\n\n"
        
        report += f"Total Activities Logged: {len(self.behaviour_log)}\n"
        report += f"Total Anomalies Detected: {self.alert_count}\n"
        report += f"Anomaly Detection Threshold: {self.anomaly_threshold}\n\n"
        
        report += "Agent Activity Summary:\n"
        report += "-" * 80 + "\n"
        
        for agent_name in self.agent_baselines.keys():
            stats = self.get_agent_statistics(agent_name)
            if stats["total_actions"] > 0:
                report += f"\n{agent_name}:\n"
                report += f"  Total Actions: {stats['total_actions']}\n"
                report += f"  Anomalies: {stats['anomalies']}\n"
                report += f"  Anomaly Rate: {stats['anomaly_rate']}\n"
                report += f"  Most Common Action: {stats['most_common_action']}\n"
        
        recent_anomalies = self.get_anomaly_report()[-5:]  # Last 5 anomalies
        if recent_anomalies:
            report += "\n" + "-" * 80 + "\n"
            report += "Recent Anomalies:\n"
            report += "-" * 80 + "\n"
            for anomaly in recent_anomalies:
                report += f"\n  {anomaly['timestamp']}\n"
                report += f"  Agent: {anomaly['agent']}\n"
                report += f"  Action: {anomaly['action']}\n"
                report += f"  Score: {anomaly['anomaly_score']:.2f}\n"
        
        report += "\n" + "="*80 + "\n"
        
        return report
    
    def simulate_security_threat(self):
        """Simulate a security threat for demonstration purposes"""
        print("\n⚠️  SIMULATING SECURITY THREAT...")
        
        # Simulate unauthorized access attempt
        self.log_activity(
            "SchedulingAgent", 
            "Attempting unauthorized access to telematics data",
            "sensor_data"  # SchedulingAgent shouldn't access sensor data
        )
        
        # Simulate suspicious action
        self.log_activity(
            "DataAnalysisAgent",
            "Attempting to drop_table customers",
            "customers"
        )
        
        # Simulate excessive activity
        for i in range(25):
            self.log_activity("DiagnosisAgent", f"Rapid action {i}", "predictions")
