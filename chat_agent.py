"""
Chat AI Agent for customer interactions
Provides personalized, context-aware responses
"""

from datetime import datetime
from typing import Dict, List, Optional
from config import SETTINGS
from providers.anthropic_provider import AnthropicProvider


class ChatAIAgent:
    """AI-powered chat agent for customer interactions"""
    
    def __init__(self, customers, vehicles, sensor_data, predictions, appointments, service_history):
        self.customers = customers
        self.vehicles = vehicles
        self.sensor_data = sensor_data
        self.predictions = predictions
        self.appointments = appointments
        self.service_history = service_history
        self.conversation_history = {}
        self.use_llm = SETTINGS.llm_enabled
        self._llm = None
        if self.use_llm and SETTINGS.llm_provider == "anthropic":
            self._llm = AnthropicProvider(model=SETTINGS.llm_model)

    async def process_message(self, customer_id: str, message: str) -> str:
        """Process customer message and generate AI response"""
        
        # Initialize conversation history
        if customer_id not in self.conversation_history:
            self.conversation_history[customer_id] = []
        
        # Log user message
        self.conversation_history[customer_id].append({
            "role": "user",
            "message": message,
            "timestamp": datetime.now().isoformat()
        })
        
        # Get customer context
        customer = self.customers.get(customer_id)
        if not customer:
            return "I'm sorry, I couldn't find your customer profile. Please contact support at 1-800-SERVICE."
        
        vehicle_id = customer.get("vehicle_id")
        vehicle = self.vehicles.get(vehicle_id)
        
        if not vehicle:
            return f"Hello {customer['name']}! I'm having trouble accessing your vehicle information. Please contact support."
        
        # Intent detection and response generation
        message_lower = message.lower()
        
        if any(word in message_lower for word in ["book", "schedule", "appointment", "service"]):
            response = self._handle_booking_request(customer, vehicle)
        
        elif any(word in message_lower for word in ["status", "health", "condition", "how is", "check"]):
            response = self._handle_status_query(customer, vehicle)
        
        elif any(word in message_lower for word in ["history", "past", "previous", "records"]):
            response = self._handle_history_query(customer, vehicle_id)
        
        elif any(word in message_lower for word in ["cancel", "reschedule", "change", "modify"]):
            response = self._handle_appointment_change(customer, vehicle_id)
        
        elif any(word in message_lower for word in ["help", "assist", "support", "what can"]):
            response = self._handle_help_request(customer)
        
        elif any(word in message_lower for word in ["problem", "issue", "warning", "error"]):
            response = self._handle_problem_report(customer, vehicle, message_lower)
        
        elif any(word in message_lower for word in ["cost", "price", "payment", "pay"]):
            response = self._handle_cost_inquiry(vehicle_id)
        
        elif any(word in message_lower for word in ["yes", "ok", "confirm", "sure"]):
            response = self._handle_confirmation(customer, vehicle)
        
        elif any(word in message_lower for word in ["no", "not now", "later", "decline"]):
            response = self._handle_decline(customer)
        
        else:
            response = self._generate_general_response(customer, vehicle, message)
        
        # Log assistant response
        self.conversation_history[customer_id].append({
            "role": "assistant",
            "message": response,
            "timestamp": datetime.now().isoformat()
        })
        
        # After computing rule-based 'response', optionally enhance via LLM
        if self._llm:
            try:
                system = (
                    "You are AutoPulse AI, a professional automotive service assistant for an Indian OEM. "
                    "Be concise, empathetic, and actionable. Use the customer's context below to tailor your reply."
                )
                context = self._build_context(customer, vehicle)
                prompt = f"Context:\n{context}\n\nUser: {message}\n\nDraft reply:\n{response}\n\nImprove the reply to be more helpful and persuasive, keeping details accurate."
                improved = self._llm.generate(prompt, system=system)
                if improved and isinstance(improved, str) and len(improved) > 10:
                    response = improved
            except Exception:
                pass
        
        return response
    
    def _build_context(self, customer: dict, vehicle: dict) -> str:
        preds = [p for p in self.predictions.values() if p.get("vehicle_id") == vehicle.get("id")]
        appts = [a for a in self.appointments.values() if a.get("customer_id") == customer.get("id")]
        last_sensor = self.sensor_data.get(vehicle.get("id"), {})
        return (
            f"Customer: {customer.get('name')} ({customer.get('phone')})\n"
            f"Vehicle: {vehicle.get('model')} {vehicle.get('model_number')} | Health: {vehicle.get('health_status')}\n"
            f"Mileage: {vehicle.get('mileage')} | Last Service: {vehicle.get('last_service_date')} | Next Due: {vehicle.get('next_service_due')}\n"
            f"Active Predictions: {[p.get('predicted_issue') for p in preds[:3]]}\n"
            f"Upcoming Appointments: {[a.get('appointment_date') for a in appts if a.get('status')=='scheduled'][:2]}\n"
            f"Latest Sensors: speed={last_sensor.get('speed')} temp={last_sensor.get('engine_temp')} battery={last_sensor.get('battery_voltage')}"
        )
    
    def _handle_booking_request(self, customer: dict, vehicle: dict) -> str:
        """Handle service booking request"""
        name = customer["name"].split()[0]
        
        # Check for existing predictions
        vehicle_predictions = [
            p for p in self.predictions.values() 
            if p["vehicle_id"] == vehicle["id"] and p["status"] in ["pending", "diagnosed"]
        ]
        
        response = f"Hi {name}! I'd be happy to help you schedule a service appointment for your {vehicle['model']}.\n\n"
        
        if vehicle_predictions:
            response += "📋 **Recommended Services Based on Our Analysis:**\n"
            for pred in vehicle_predictions[:3]:
                response += f"  • {pred['predicted_issue']} (Priority: {pred['priority']})\n"
            response += "\n"
        
        response += f"🚗 **Vehicle Status:**\n"
        response += f"  • Current health: {vehicle['health_status'].replace('_', ' ').title()}\n"
        response += f"  • Mileage: {vehicle.get('mileage', 0):,} miles\n"
        response += f"  • Last service: {vehicle.get('last_service_date', 'N/A')}\n"
        response += f"  • Next service due: {vehicle.get('next_service_due', 'Not scheduled')}\n\n"
        
        response += "📍 **Available Service Centers:**\n"
        response += "  • Main Service Center (highest capacity)\n"
        response += "  • North Branch\n"
        response += "  • South Branch\n\n"
        
        response += "Would you like me to show you available time slots? Just say 'Yes' and I'll find the best options for you!"
        
        return response
    
    def _handle_status_query(self, customer: dict, vehicle: dict) -> str:
        """Handle vehicle status query"""
        name = customer["name"].split()[0]
        
        response = f"Hi {name}! Here's the current status of your {vehicle['model']}:\n\n"
        
        # Vehicle health
        health_status = vehicle['health_status'].replace('_', ' ').title()
        health_emoji = "✅" if "good" in vehicle['health_status'] or "excellent" in vehicle['health_status'] else "⚠️"
        
        response += f"🚗 **Overall Health:** {health_emoji} {health_status}\n"
        response += f"📊 **Mileage:** {vehicle.get('mileage', 0):,} miles\n"
        response += f"🔧 **Last Service:** {vehicle.get('last_service_date', 'N/A')}\n"
        response += f"📅 **Next Service Due:** {vehicle.get('next_service_due', 'Not scheduled')}\n\n"
        
        # Real-time sensor data
        sensor = self.sensor_data.get(vehicle["id"])
        if sensor:
            response += "📡 **Real-Time Diagnostics:**\n"
            response += f"  • Engine Temperature: {sensor.get('engine_temp', 'N/A')}°F\n"
            response += f"  • Oil Pressure: {sensor.get('oil_pressure', 'N/A')} PSI\n"
            response += f"  • Battery Voltage: {sensor.get('battery_voltage', 'N/A')}V\n"
            response += f"  • Fuel Level: {sensor.get('fuel_level', 'N/A')}%\n"
            
            tire_pressure = sensor.get('tire_pressure', {})
            if tire_pressure:
                response += f"  • Tire Pressure: FL:{tire_pressure.get('front_left', 'N/A')} FR:{tire_pressure.get('front_right', 'N/A')} "
                response += f"RL:{tire_pressure.get('rear_left', 'N/A')} RR:{tire_pressure.get('rear_right', 'N/A')} PSI\n"
            
            error_codes = sensor.get('error_codes', [])
            if error_codes:
                response += f"  • ⚠️ Error Codes: {', '.join(error_codes)}\n"
            else:
                response += f"  • ✅ No error codes detected\n"
        
        # Predicted issues
        vehicle_predictions = [
            p for p in self.predictions.values() 
            if p["vehicle_id"] == vehicle["id"] and p["status"] in ["pending", "diagnosed"]
        ]
        
        if vehicle_predictions:
            response += "\n⚠️ **Predicted Maintenance Needs:**\n"
            for pred in vehicle_predictions[:3]:
                priority_emoji = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}.get(pred['priority'], "⚪")
                response += f"  {priority_emoji} {pred['predicted_issue']} (Confidence: {pred['confidence_score']:.0%})\n"
                response += f"     Parts at risk: {pred['parts_at_risk']}\n"
                response += f"     Recommended: {pred['recommended_action']}\n"
        else:
            response += "\n✅ No immediate maintenance needs detected. Your vehicle is running well!"
        
        response += "\n💬 Would you like to schedule a service appointment or need more information?"
        
        return response
    
    def _handle_history_query(self, customer: dict, vehicle_id: str) -> str:
        """Handle service history query"""
        name = customer["name"].split()[0]
        
        history = [s for s in self.service_history.values() if s["vehicle_id"] == vehicle_id]
        
        if not history:
            return f"Hi {name}! I don't see any service history for your vehicle yet. " \
                   "This might be a new vehicle, or services haven't been logged in our system."
        
        response = f"Hi {name}! Here's your service history:\n\n"
        response += "📋 **Service Records:**\n"
        
        sorted_history = sorted(history, key=lambda x: x["service_date"], reverse=True)[:10]
        
        total_cost = 0
        for service in sorted_history:
            response += f"\n  **{service['service_date']}** - {service['service_type']}\n"
            response += f"    Status: {service['status'].title()}\n"
            
            cost = service.get('cost', 0)
            if cost > 0:
                response += f"    Cost: ${cost:.2f}\n"
                total_cost += cost
            
            if service.get('technician'):
                response += f"    Technician: {service['technician']}\n"
            
            if service.get('parts_replaced'):
                response += f"    Parts Replaced: {service['parts_replaced']}\n"
            
            if service.get('customer_rating'):
                response += f"    Your Rating: {'⭐' * service['customer_rating']}\n"
        
        if total_cost > 0:
            response += f"\n💰 **Total Service Costs:** ${total_cost:.2f}\n"
        
        response += f"\n📊 **Total Services:** {len(history)}\n"
        
        return response
    
    def _handle_appointment_change(self, customer: dict, vehicle_id: str) -> str:
        """Handle appointment cancellation/rescheduling"""
        name = customer["name"].split()[0]
        
        appointments = [
            a for a in self.appointments.values() 
            if a["vehicle_id"] == vehicle_id and a["status"] == "scheduled"
        ]
        
        if not appointments:
            return f"Hi {name}! You don't have any scheduled appointments at the moment. " \
                   "Would you like to book a new appointment?"
        
        response = f"Hi {name}! Here are your upcoming appointments:\n\n"
        
        for apt in appointments:
            response += f"📅 **{apt['appointment_date']} at {apt['appointment_time']}**\n"
            response += f"    Service: {apt['service_type']}\n"
            response += f"    Location: {apt['service_center']}\n"
            response += f"    Priority: {apt['priority'].title()}\n\n"
        
        response += "To cancel or reschedule, please tell me:\n"
        response += "  • Type 'CANCEL' to cancel an appointment\n"
        response += "  • Type 'RESCHEDULE' to change the date/time\n"
        response += "  • Or call us at 1-800-SERVICE for immediate assistance"
        
        return response
    
    def _handle_help_request(self, customer: dict) -> str:
        """Handle general help request"""
        name = customer["name"].split()[0]
        
        return f"Hi {name}! I'm your AI vehicle maintenance assistant. Here's how I can help:\n\n" \
               "🔹 **Vehicle Status** - Check your vehicle's health and diagnostics\n" \
               "🔹 **Book Service** - Schedule maintenance appointments\n" \
               "🔹 **Service History** - View past maintenance records\n" \
               "🔹 **Appointments** - Manage upcoming service appointments\n" \
               "🔹 **Predict Issues** - Get AI-powered maintenance predictions\n" \
               "🔹 **Cost Estimates** - Get pricing information\n" \
               "🔹 **Emergency Support** - Urgent vehicle issues\n\n" \
               "💬 Just ask me anything like:\n" \
               "  • 'How is my car doing?'\n" \
               "  • 'I need to schedule service'\n" \
               "  • 'Show my service history'\n" \
               "  • 'What's wrong with my car?'\n\n" \
               "I'm here 24/7 to help you! What would you like to know?"
    
    def _handle_problem_report(self, customer: dict, vehicle: dict, message: str) -> str:
        """Handle customer reporting a problem"""
        name = customer["name"].split()[0]
        
        response = f"Hi {name}, thanks for letting me know about the issue with your {vehicle['model']}.\n\n"
        
        # Try to identify the problem type
        if any(word in message for word in ["noise", "sound", "loud"]):
            response += "🔊 I see you're experiencing unusual noises. This could indicate:\n"
            response += "  • Worn brake pads\n"
            response += "  • Engine issues\n"
            response += "  • Exhaust system problems\n\n"
        
        elif any(word in message for word in ["shake", "vibrate", "vibration"]):
            response += "📳 Vibrations can be caused by:\n"
            response += "  • Tire balance issues\n"
            response += "  • Suspension problems\n"
            response += "  • Brake rotor issues\n\n"
        
        elif any(word in message for word in ["leak", "fluid", "drip"]):
            response += "💧 Fluid leaks require immediate attention. Common sources:\n"
            response += "  • Oil leaks\n"
            response += "  • Coolant leaks\n"
            response += "  • Brake fluid\n\n"
        
        elif any(word in message for word in ["light", "warning", "dashboard"]):
            response += "⚠️ Dashboard warning lights should be checked promptly.\n\n"
        
        response += "🔧 **Recommended Action:**\n"
        response += "I recommend scheduling an inspection as soon as possible. "
        response += "Our technicians can diagnose the issue and provide a solution.\n\n"
        response += "Would you like me to book an urgent appointment for you? (Reply 'YES')"
        
        return response
    
    def _handle_cost_inquiry(self, vehicle_id: str) -> str:
        """Handle cost and pricing inquiries"""
        response = "💰 **Typical Service Costs:**\n\n"
        response += "**Routine Maintenance:**\n"
        response += "  • Oil Change: $45 - $85\n"
        response += "  • Tire Rotation: $35 - $50\n"
        response += "  • Air Filter Replacement: $25 - $50\n"
        response += "  • Brake Inspection: $Free - $30\n\n"
        response += "**Common Repairs:**\n"
        response += "  • Brake Pad Replacement: $150 - $300\n"
        response += "  • Battery Replacement: $100 - $200\n"
        response += "  • Alternator Replacement: $350 - $600\n"
        response += "  • Starter Replacement: $300 - $500\n\n"
        response += "**Diagnostic Services:**\n"
        response += "  • Computer Diagnostic: $75 - $150\n"
        response += "  • Comprehensive Inspection: $100 - $200\n\n"
        response += "💡 *Actual costs may vary based on your specific vehicle model and required parts.*\n\n"
        response += "Would you like a specific quote for your vehicle? Let me know what service you need!"
        
        return response
    
    def _handle_confirmation(self, customer: dict, vehicle: dict) -> str:
        """Handle customer confirmation"""
        name = customer["name"].split()[0]
        
        return f"Great, {name}! I'm processing your request for your {vehicle['model']}.\n\n" \
               "📅 I'll find the best available appointment slots for you. " \
               "You should receive a confirmation shortly with:\n" \
               "  • Appointment date and time\n" \
               "  • Service center location\n" \
               "  • Estimated service duration\n" \
               "  • What to expect during your visit\n\n" \
               "You'll also receive:\n" \
               "  📧 Email confirmation\n" \
               "  📱 SMS reminder 24 hours before\n" \
               "  🔔 App notification\n\n" \
               "Is there anything else I can help you with?"
    
    def _handle_decline(self, customer: dict) -> str:
        """Handle customer declining service"""
        name = customer["name"].split()[0]
        
        return f"No problem, {name}! I understand. \n\n" \
               "⏰ I'll check back with you in a few days to see if you'd like to schedule then. " \
               "In the meantime, please keep an eye on your vehicle's performance.\n\n" \
               "📞 If anything changes or you have an emergency, don't hesitate to:\n" \
               "  • Chat with me anytime (24/7 available)\n" \
               "  • Call us at 1-800-SERVICE\n" \
               "  • Use the mobile app for quick booking\n\n" \
               "Your safety is our priority. Drive safely! 🚗"
    
    def _generate_general_response(self, customer: dict, vehicle: dict, message: str) -> str:
        """Generate general response for unclassified queries"""
        name = customer["name"].split()[0]
        
        return f"Thanks for reaching out, {name}! \n\n" \
               f"I'm here to help with your {vehicle['model']}. While I'm not sure I fully understood your question, " \
               "I can definitely assist with:\n\n" \
               "  • Checking your vehicle's status\n" \
               "  • Booking service appointments\n" \
               "  • Reviewing service history\n" \
               "  • Answering maintenance questions\n\n" \
               "Could you rephrase your question or let me know which of these areas you'd like help with?"
    
    def get_conversation_history(self, customer_id: str) -> List[Dict]:
        """Retrieve conversation history for a customer"""
        return self.conversation_history.get(customer_id, [])
    
    def clear_conversation_history(self, customer_id: str):
        """Clear conversation history for a customer"""
        if customer_id in self.conversation_history:
            del self.conversation_history[customer_id]
