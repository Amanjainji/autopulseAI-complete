"""
AI Agent System for Predictive Vehicle Maintenance
Contains all Worker Agents and Master Agent orchestration
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional
import random
import asyncio
import sqlite3


class DataAnalysisAgent:
    """Analyzes streaming vehicle telematics and sensor data to detect early warning signs"""
    
    def __init__(self, ueba, vehicles, sensor_data, predictions):
        self.ueba = ueba
        self.vehicles = vehicles
        self.sensor_data = sensor_data
        self.predictions = predictions
    
    async def run(self):
        if not self.ueba.log_activity("DataAnalysisAgent", "Analyzing sensor data", "sensor_data"):
            return
        
        print("\n🔍 [DataAnalysisAgent] Starting analysis...")
        
        for v_id, vehicle in self.vehicles.items():
            # Get latest sensor data
            sensor = self.sensor_data.get(v_id)
            if not sensor:
                continue
            
            # Analyze sensor patterns
            issues = []
            
            if sensor.get("engine_temp", 0) > 100:
                issues.append("Engine overheating detected")
            
            if sensor.get("oil_pressure", 0) < 30:
                issues.append("Low oil pressure")
            
            if sensor.get("battery_voltage", 0) < 12.5:
                issues.append("Weak battery voltage")
            
            tire_pressure = sensor.get("tire_pressure", {})
            if any(p < 28 for p in tire_pressure.values()):
                issues.append("Low tire pressure detected")
            
            if sensor.get("error_codes", []):
                issues.append(f"Diagnostic codes: {', '.join(sensor['error_codes'])}")
            
            # Forecast maintenance needs based on mileage
            if vehicle.get("mileage", 0) > 45000:
                issues.append("High mileage - comprehensive inspection recommended")
            
            if issues:
                vehicle["health_status"] = "needs_attention"
                self.vehicles[v_id] = vehicle
                print(f"   ⚠️ Vehicle {vehicle['model']} ({v_id}): {', '.join(issues[:2])}")
                
                # Create predictions
                for issue in issues[:2]:  # Limit to top 2 issues
                    pred_id = f"PRED-{v_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}-{random.randint(1000,9999)}"
                    self.predictions[pred_id] = {
                        "id": pred_id,
                        "vehicle_id": v_id,
                        "prediction_date": datetime.now().strftime("%Y-%m-%d"),
                        "predicted_issue": issue,
                        "confidence_score": round(random.uniform(0.7, 0.95), 2),
                        "priority": "high" if any(x in issue.lower() for x in ["overheat", "brake", "critical"]) else "medium",
                        "estimated_failure_date": (datetime.now() + timedelta(days=random.randint(7, 30))).strftime("%Y-%m-%d"),
                        "recommended_action": f"Schedule service for {issue}",
                        "parts_at_risk": self._identify_parts(issue),
                        "status": "pending"
                    }
        
        await asyncio.sleep(0.1)
    
    def _identify_parts(self, issue: str) -> str:
        """Identify parts at risk based on issue"""
        if "engine" in issue.lower():
            return "Engine components, cooling system"
        elif "oil" in issue.lower():
            return "Oil pump, oil filter"
        elif "battery" in issue.lower():
            return "Battery, alternator"
        elif "tire" in issue.lower():
            return "Tires, TPMS sensors"
        elif "brake" in issue.lower():
            return "Brake pads, rotors"
        return "To be determined"


class DiagnosisAgent:
    """Runs predictive models to assess probable component failures"""
    
    def __init__(self, ueba, vehicles, predictions):
        self.ueba = ueba
        self.vehicles = vehicles
        self.predictions = predictions
    
    async def run(self):
        if not self.ueba.log_activity("DiagnosisAgent", "Running diagnostic models", "predictions"):
            return
        
        print("\n🩺 [DiagnosisAgent] Running diagnostics...")
        
        diagnosed_count = 0
        for pred_id, prediction in list(self.predictions.items()):
            if prediction["status"] != "pending":
                continue
            
            vehicle = self.vehicles.get(prediction["vehicle_id"])
            if not vehicle:
                continue
            
            # Calculate failure probability
            failure_prob = self._calculate_failure_probability(vehicle, prediction["predicted_issue"])
            
            # Update priority
            if failure_prob > 0.8:
                prediction["priority"] = "critical"
                priority_msg = "🔴 CRITICAL"
            elif failure_prob > 0.6:
                prediction["priority"] = "high"
                priority_msg = "🟠 HIGH"
            elif failure_prob > 0.4:
                prediction["priority"] = "medium"
                priority_msg = "🟡 MEDIUM"
            else:
                prediction["priority"] = "low"
                priority_msg = "🟢 LOW"
            
            print(f"   {priority_msg} - {vehicle['model']}: {prediction['predicted_issue']}")
            print(f"      Failure Probability: {failure_prob:.1%} | Confidence: {prediction['confidence_score']:.1%}")
            
            prediction["status"] = "diagnosed"
            self.predictions[pred_id] = prediction
            diagnosed_count += 1
        
        if diagnosed_count > 0:
            print(f"   ✅ Diagnosed {diagnosed_count} potential issues")
        
        await asyncio.sleep(0.1)
    
    def _calculate_failure_probability(self, vehicle: dict, issue: str) -> float:
        """Calculate failure probability"""
        base_prob = 0.5
        
        mileage = vehicle.get("mileage", 0)
        if mileage > 50000:
            base_prob += 0.2
        elif mileage > 30000:
            base_prob += 0.1
        
        if vehicle.get("health_status") == "critical":
            base_prob += 0.3
        elif vehicle.get("health_status") == "needs_attention":
            base_prob += 0.2
        
        if any(keyword in issue.lower() for keyword in ["critical", "failure", "overheat", "brake"]):
            base_prob += 0.2
        
        return min(base_prob, 0.95)


class CustomerEngagementAgent:
    """Initiates personalized conversations with vehicle owners"""
    
    def __init__(self, ueba, customers, vehicles, predictions, voice_agent=None):
        self.ueba = ueba
        self.customers = customers
        self.vehicles = vehicles
        self.predictions = predictions
        self.voice_agent = voice_agent
    
    async def run(self):
        if not self.ueba.log_activity("CustomerEngagementAgent", "Engaging customers", "customers"):
            return
        
        print("\n💬 [CustomerEngagementAgent] Reaching out to customers...")
        
        contacted_count = 0
        for pred_id, prediction in list(self.predictions.items()):
            if prediction["status"] != "diagnosed":
                continue
            
            vehicle_id = prediction["vehicle_id"]
            vehicle = self.vehicles.get(vehicle_id)
            customer = next((c for c in self.customers.values() if c.get("vehicle_id") == vehicle_id), None)
            
            if not customer or not vehicle:
                continue
            
            # Generate personalized message
            message = self._generate_message(customer, vehicle, prediction)
            
            print(f"\n   📱 Contacting {customer['name']} ({customer['phone']})")
            print(f"   🚗 Vehicle: {vehicle['model']}")
            print(f"   📋 Issue: {prediction['predicted_issue']} (Priority: {prediction['priority']})")
            
            if self.voice_agent and prediction.get("priority") in {"critical", "high"}:
                await self._initiate_voice_outreach(customer, vehicle, prediction, message)

            prediction["status"] = "customer_contacted"
            self.predictions[pred_id] = prediction
            contacted_count += 1
        
        if contacted_count > 0:
            print(f"\n   ✅ Contacted {contacted_count} customers")
        
        await asyncio.sleep(0.1)
    
    def _generate_message(self, customer: dict, vehicle: dict, prediction: dict) -> str:
        """Generate persuasive message"""
        name = customer["name"].split()[0]
        issue = prediction["predicted_issue"]
        priority = prediction["priority"]
        
        if priority == "critical":
            opening = f"Hello {name}, URGENT notification about your {vehicle['model']}."
            concern = f"Critical issue detected: {issue}. Immediate attention required for safety."
            action = "Please schedule service within 2-3 days."
        elif priority == "high":
            opening = f"Hi {name}, important update about your {vehicle['model']}."
            concern = f"Issue identified: {issue}. Address soon to prevent costly repairs."
            action = "Recommend scheduling service within the next week."
        else:
            opening = f"Hi {name}, routine maintenance reminder for your {vehicle['model']}."
            concern = f"Noticed: {issue}. Not urgent, but keeping up will ensure smooth operation."
            action = "Schedule a convenient service appointment."
        
        return f"{opening} {concern} {action}"

    async def _initiate_voice_outreach(self, customer: dict, vehicle: dict, prediction: dict, message: str) -> None:
        try:
            script = await self.voice_agent.place_outbound_call(
                customer=customer,
                vehicle=vehicle,
                prediction=prediction,
                message=message,
            )
            prediction["voice_call_id"] = script.call_id
        except Exception as exc:
            print(f"   ⚠️ Voice outreach failed: {exc}")


class SchedulingAgent:
    """Manages appointment scheduling"""
    
    def __init__(self, ueba, customers, vehicles, predictions, appointments):
        self.ueba = ueba
        self.customers = customers
        self.vehicles = vehicles
        self.predictions = predictions
        self.appointments = appointments
        self.service_centers = self._init_service_centers()
    
    def _init_service_centers(self):
        """Initialize service centers with availability"""
        time_slots = ["09:00 AM", "10:30 AM", "12:00 PM", "02:00 PM", "03:30 PM"]
        centers = {}
        
        for center_name in ["Main Service Center", "North Branch", "South Branch"]:
            slots = []
            for day in range(1, 15):
                date = datetime.now() + timedelta(days=day)
                if date.weekday() < 5:  # Weekdays only
                    for time in time_slots:
                        if random.random() > 0.3:
                            slots.append(f"{date.strftime('%Y-%m-%d')} {time}")
            centers[center_name] = {"available_slots": slots}
        
        return centers
    
    async def run(self):
        if not self.ueba.log_activity("SchedulingAgent", "Scheduling appointments", "appointments"):
            return
        
        print("\n📅 [SchedulingAgent] Managing appointments...")
        
        scheduled_count = 0
        declined_count = 0
        
        for pred_id, prediction in list(self.predictions.items()):
            if prediction["status"] not in {"customer_contacted", "voice_confirmed"}:
                continue
            
            vehicle_id = prediction["vehicle_id"]
            vehicle = self.vehicles.get(vehicle_id)
            customer = next((c for c in self.customers.values() if c.get("vehicle_id") == vehicle_id), None)
            
            if not customer or not vehicle:
                continue
            
            # Simulate customer response
            customer_accepts = random.random() > 0.15  # 85% acceptance
            
            if customer_accepts:
                priority = prediction["priority"]
                days_ahead = 2 if priority == "critical" else 5 if priority == "high" else 10
                
                center_name = list(self.service_centers.keys())[0]
                slot = self._get_slot(center_name, days_ahead)
                
                if slot:
                    appointment_id = f"APT-{datetime.now().strftime('%Y%m%d%H%M%S')}-{random.randint(1000,9999)}"
                    date_part, time_part = slot.split(' ', 1)
                    
                    self.appointments[appointment_id] = {
                        "id": appointment_id,
                        "vehicle_id": vehicle_id,
                        "customer_id": customer["id"],
                        "appointment_date": date_part,
                        "appointment_time": time_part,
                        "service_type": prediction["predicted_issue"],
                        "status": "scheduled",
                        "priority": priority,
                        "service_center": center_name,
                        "estimated_duration": 90 if priority in ["critical", "high"] else 60,
                        "estimated_cost": round(random.uniform(120.0, 450.0), 2),
                        "created_at": datetime.now().isoformat(),
                        "notes": f"Scheduled automatically based on {prediction['predicted_issue']}",
                        "assigned_technician": f"Tech-{random.randint(1, 10)}"
                    }
                    
                    prediction["status"] = "appointment_scheduled"
                    self.predictions[pred_id] = prediction
                    
                    print(f"   ✅ {customer['name']}: {date_part} at {time_part} ({priority.upper()})")
                    scheduled_count += 1
            else:
                print(f"   ❌ {customer['name']} declined (will follow up)")
                prediction["status"] = "declined"
                self.predictions[pred_id] = prediction
                declined_count += 1
        
        if scheduled_count > 0 or declined_count > 0:
            print(f"\n   📊 Scheduled: {scheduled_count} | Declined: {declined_count}")
        
        await asyncio.sleep(0.1)
    
    def _get_slot(self, center_name: str, days_ahead: int) -> Optional[str]:
        """Get available slot"""
        center = self.service_centers[center_name]
        target_date = datetime.now() + timedelta(days=days_ahead)
        
        for slot in center["available_slots"]:
            slot_date = datetime.strptime(slot.split()[0], '%Y-%m-%d')
            if slot_date <= target_date:
                center["available_slots"].remove(slot)
                return slot
        
        if center["available_slots"]:
            slot = center["available_slots"][0]
            center["available_slots"].remove(slot)
            return slot
        
        return None


class FeedbackAgent:
    """Collects post-service feedback"""
    
    def __init__(self, ueba, customers, vehicles, service_history):
        self.ueba = ueba
        self.customers = customers
        self.vehicles = vehicles
        self.service_history = service_history
    
    async def run(self):
        if not self.ueba.log_activity("FeedbackAgent", "Collecting feedback", "service_records"):
            return
        
        print("\n📊 [FeedbackAgent] Collecting feedback...")
        
        feedback_count = 0
        for srv_id, service in self.service_history.items():
            if service.get("status") == "completed" and service.get("customer_rating", 0) == 0:
                vehicle_id = service["vehicle_id"]
                customer = next((c for c in self.customers.values() if c.get("vehicle_id") == vehicle_id), None)
                
                if customer:
                    rating = random.randint(4, 5)
                    service["customer_rating"] = rating
                    self.service_history[srv_id] = service
                    
                    print(f"   ⭐ {customer['name']}: {rating}/5 for {service['service_type']}")
                    feedback_count += 1
                    
                    # Update vehicle status
                    if vehicle_id in self.vehicles:
                        self.vehicles[vehicle_id]["health_status"] = "good"
        
        if feedback_count > 0:
            print(f"   ✅ Collected {feedback_count} feedback responses")
        
        await asyncio.sleep(0.1)


class ManufacturingInsightsAgent:
    """RCA/CAPA analysis for manufacturing feedback"""
    
    def __init__(self, ueba, vehicles, predictions):
        self.ueba = ueba
        self.vehicles = vehicles
        self.predictions = predictions
    
    async def run(self):
        if not self.ueba.log_activity("ManufacturingInsightsAgent", "Analyzing patterns", "manufacturing_feedback"):
            return
        
        print("\n🏭 [ManufacturingInsightsAgent] Analyzing defect patterns...")
        
        # Find recurring issues
        defect_patterns = {}
        
        for prediction in self.predictions.values():
            vehicle = self.vehicles.get(prediction["vehicle_id"])
            if not vehicle:
                continue
            
            model = vehicle["model"]
            issue = prediction["predicted_issue"]
            key = f"{model}:{issue}"
            
            if key not in defect_patterns:
                defect_patterns[key] = {"model": model, "issue": issue, "count": 0}
            
            defect_patterns[key]["count"] += 1
        
        # Generate insights for recurring defects
        for key, pattern in defect_patterns.items():
            if pattern["count"] >= 2:  # Recurring threshold
                root_cause = self._identify_root_cause(pattern["issue"])
                corrective = self._corrective_action(pattern["issue"])
                preventive = self._preventive_action(pattern["issue"])
                
                print(f"\n   🔧 Recurring Defect Alert:")
                print(f"      Model: {pattern['model']}")
                print(f"      Issue: {pattern['issue']}")
                print(f"      Occurrences: {pattern['count']}")
                print(f"      Root Cause: {root_cause}")
                print(f"      Corrective: {corrective}")
                print(f"      Preventive: {preventive}")
        
        await asyncio.sleep(0.1)
    
    def _identify_root_cause(self, issue: str) -> str:
        """Identify root cause"""
        if "engine" in issue.lower() or "overheat" in issue.lower():
            return "Inadequate cooling system capacity"
        elif "oil" in issue.lower():
            return "Oil pump specification insufficient"
        elif "battery" in issue.lower():
            return "Alternator output inadequate"
        elif "tire" in issue.lower():
            return "TPMS calibration issue"
        return "Requires detailed investigation"
    
    def _corrective_action(self, issue: str) -> str:
        """Suggest corrective action"""
        if "engine" in issue.lower():
            return "Upgrade cooling system components"
        elif "oil" in issue.lower():
            return "Replace oil pumps with higher spec"
        elif "battery" in issue.lower():
            return "Install higher capacity batteries"
        return "Issue recall and free repair"
    
    def _preventive_action(self, issue: str) -> str:
        """Suggest preventive action"""
        if "engine" in issue.lower():
            return "Redesign cooling system with 20% higher capacity"
        elif "oil" in issue.lower():
            return "Update oil pump specifications"
        elif "battery" in issue.lower():
            return "Improve charging system design"
        return "Enhance quality control processes"


class MasterAgent:
    """Main orchestrator coordinating all Worker Agents"""
    
    def __init__(self, ueba):
        self.ueba = ueba
        self.workers = {}
        self.loop_running = False
        self.cycle_count = 0
    
    def register_worker(self, name: str, worker):
        """Register a worker agent"""
        if self.ueba.log_activity("MasterAgent", f"Registering: {name}", "all"):
            self.workers[name] = worker
            print(f"✅ [MasterAgent] Registered: {name}")
    
    async def orchestrate(self):
        """Main orchestration loop"""
        print("\n" + "="*80)
        print("🎯 MASTER AGENT - Starting Orchestration")
        print("="*80)
        
        self.loop_running = True
        
        while self.loop_running:
            self.cycle_count += 1
            
            print(f"\n{'='*80}")
            print(f"🔄 Cycle #{self.cycle_count} - {datetime.now().strftime('%H:%M:%S')}")
            print(f"{'='*80}")
            
            if not self.ueba.log_activity("MasterAgent", "Orchestration cycle", "all"):
                print("⚠️ Security check failed, pausing")
                await asyncio.sleep(30)
                continue
            
            # Execute workers in sequence
            for name in ["DataAnalysis", "Diagnosis", "CustomerEngagement", "Scheduling", "Feedback", "ManufacturingInsights"]:
                if name in self.workers:
                    try:
                        await self.workers[name].run()
                    except Exception as e:
                        print(f"❌ Error in {name}: {str(e)}")
            
            print(f"\n{'='*80}")
            print(f"✅ Cycle #{self.cycle_count} Complete")
            print(f"{'='*80}\n")
            
            await asyncio.sleep(20)  # Wait before next cycle
    
    def stop(self):
        """Stop orchestration"""
        self.loop_running = False
