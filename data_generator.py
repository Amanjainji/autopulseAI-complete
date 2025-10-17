"""
Synthetic Vehicle Data Generator
Generates sample data for 10 vehicles with complete telemetry, service history, etc.
"""

from datetime import datetime, timedelta
import random
from typing import Dict, List


class VehicleDataGenerator:
    """Generates synthetic data for demonstration"""
    
    @staticmethod
    def generate_sample_vehicles() -> List[Dict]:
        """Generate complete data for 10 sample vehicles"""
        
        vehicle_models = [
            ("Mahindra Scorpio N", "SCORPIO-N", "Full-size ladder-frame SUV"),
            ("Tata Nexon EV", "NEXON-EV", "Compact electric SUV"),
            ("Maruti Grand Vitara", "GRAND-VITARA", "Strong hybrid SUV"),
            ("Hyundai Creta", "CRETA-2025", "Urban crossover SUV"),
            ("Kia Seltos", "SELTOS-GT", "GT Line turbo variant"),
            ("Mahindra XUV700", "XUV700-AX7", "ADAS equipped flagship"),
            ("Toyota Innova Hycross", "INNOVA-HYCROSS", "Premium family MPV"),
            ("Skoda Slavia", "SLAVIA-TSI", "1.5 TSI sedan"),
            ("Honda Elevate", "ELEVATE-ZX", "Compact lifestyle SUV"),
            ("MG Hector", "HECTOR-SMART", "Connected SUV with i-SMART")
        ]

        indian_addresses = [
            ("32 MG Road", "Bengaluru", "KA", "560001"),
            ("14 Napean Sea Road", "Mumbai", "MH", "400006"),
            ("221 Park Street", "Kolkata", "WB", "700017"),
            ("9 Lodhi Estate", "New Delhi", "DL", "110003"),
            ("508 Lawsons Bay Colony", "Visakhapatnam", "AP", "530017"),
            ("17 Boat Club Road", "Pune", "MH", "411001"),
            ("44 RK Beach Road", "Chennai", "TN", "600004"),
            ("76 Jubilee Hills", "Hyderabad", "TS", "500033"),
            ("58 VIP Road", "Guwahati", "AS", "781015"),
            ("91 Civil Lines", "Lucknow", "UP", "226001")
        ]

        phone_numbers = [
            "+91-98765-43210",
            "+91-98197-22445",
            "+91-98305-11990",
            "+91-98711-77889",
            "+91-98493-66780",
            "+91-98902-14567",
            "+91-98840-23589",
            "+91-98490-77881",
            "+91-94350-66789",
            "+91-99199-34560"
        ]
        
        vehicles_data = []
        
        for i, (model, model_num, description) in enumerate(vehicle_models, 1):
            vehicle_id = f"VEH{i:03d}"
            customer_id = f"CUST-{i:03d}"
            
            # Customer data
            purchase_date = datetime.now() - timedelta(days=random.randint(30, 730))
            
            street, city, state_code, pin = indian_addresses[i-1]

            customer = {
                "id": customer_id,
                "name": VehicleDataGenerator._generate_name(i),
                "phone": phone_numbers[i-1],
                "email": f"{VehicleDataGenerator._generate_email_alias(i)}@autopulse.in",
                "address": f"{street}, {city}, {state_code} {pin}",
                "purchase_date": purchase_date.strftime("%Y-%m-%d"),
                "vehicle_id": vehicle_id
            }
            
            # Vehicle data
            last_service = purchase_date + timedelta(days=random.randint(90, 180))
            
            vehicle = {
                "id": vehicle_id,
                "customer_id": customer_id,
                "model": model,
                "model_number": model_num,
                "vin": f"ME{random.randint(10,99)}{random.randint(100000,999999)}",
                "registration_number": VehicleDataGenerator._generate_registration(state_code),
                "manufacturing_date": (purchase_date - timedelta(days=45)).strftime("%Y-%m-%d"),
                "purchase_date": customer["purchase_date"],
                "warranty_expiry": (purchase_date + timedelta(days=1095)).strftime("%Y-%m-%d"),
                "mileage": random.randint(5000, 50000),
                "health_status": random.choice(["excellent", "good", "good", "needs_attention"]),
                "last_service_date": last_service.strftime("%Y-%m-%d"),
                "next_service_due": (last_service + timedelta(days=180)).strftime("%Y-%m-%d")
            }
            
            # Sensor data with realistic values
            base_temp = 90.0
            temp_variance = random.uniform(-5, 20)  # Some vehicles will show overheating
            
            sensor_data = {
                "vehicle_id": vehicle_id,
                "timestamp": datetime.now().isoformat(),
                "engine_temp": round(base_temp + temp_variance, 2),
                "oil_pressure": round(random.uniform(25.0, 65.0), 2),
                "battery_voltage": round(random.uniform(12.0, 14.5), 2),
                "tire_pressure": {
                    "front_left": round(random.uniform(28.0, 35.0), 1),
                    "front_right": round(random.uniform(28.0, 35.0), 1),
                    "rear_left": round(random.uniform(28.0, 35.0), 1),
                    "rear_right": round(random.uniform(28.0, 35.0), 1)
                },
                "fuel_level": round(random.uniform(10.0, 95.0), 1),
                "speed": round(random.uniform(0.0, 75.0), 1),
                "rpm": round(random.uniform(800.0, 3500.0), 0),
                "error_codes": VehicleDataGenerator._generate_error_codes(i)
            }
            
            # Service history
            service_history = []
            num_services = random.randint(1, 5)
            
            for j in range(num_services):
                service_date = last_service - timedelta(days=j*180)
                service_history.append({
                    "id": f"SRV{i:03d}{j:02d}",
                    "vehicle_id": vehicle_id,
                    "service_date": service_date.strftime("%Y-%m-%d"),
                    "service_type": random.choice([
                        "Oil Change", 
                        "Tire Rotation", 
                        "Brake Inspection",
                        "Engine Diagnostic",
                        "Transmission Service",
                        "Air Filter Replacement"
                    ]),
                    "status": "completed",
                    "technician": f"Tech-{random.randint(1, 15)}",
                    "cost": round(random.uniform(50.0, 500.0), 2),
                    "parts_replaced": random.choice([
                        "Oil Filter",
                        "Air Filter",
                        "Brake Pads",
                        "Spark Plugs",
                        "Battery",
                        "None"
                    ]),
                    "remarks": "Service completed successfully. All systems functioning normally.",
                    "customer_rating": random.randint(4, 5)
                })
            
            vehicles_data.append({
                "customer": customer,
                "vehicle": vehicle,
                "sensor_data": sensor_data,
                "service_history": service_history
            })
        
        return vehicles_data
    
    @staticmethod
    def _generate_name(index: int) -> str:
        """Generate realistic customer names"""
        first_names = [
            "Amaan", "Neha", "Arjun", "Priya", "Rohan",
            "Ishita", "Vikram", "Sneha", "Aditya", "Meera"
        ]
        last_names = [
            "Jain", "Iyer", "Singh", "Menon", "Patel",
            "Sharma", "Kulkarni", "Nair", "Verma", "Kapoor"
        ]

        return f"{first_names[(index-1) % len(first_names)]} {last_names[(index-1) % len(last_names)]}"

    @staticmethod
    def _generate_email_alias(index: int) -> str:
        first_names = [
            "amaan", "neha", "arjun", "priya", "rohan",
            "ishita", "vikram", "sneha", "aditya", "meera"
        ]
        last_names = [
            "jain", "iyer", "singh", "menon", "patel",
            "sharma", "kulkarni", "nair", "verma", "kapoor"
        ]

        first = first_names[(index-1) % len(first_names)]
        last = last_names[(index-1) % len(last_names)]
        return f"{first}.{last}"

    @staticmethod
    def _generate_registration(state_code: str) -> str:
        series = random.choice(["AA", "AB", "BT", "CR", "DX", "EZ"])
        return f"{state_code}{random.randint(10,99)}{series}{random.randint(1000,9999)}"
    
    @staticmethod
    def _generate_error_codes(vehicle_index: int) -> List[str]:
        """Generate diagnostic trouble codes (DTCs)"""
        # Some vehicles have no errors
        if random.random() > 0.4:
            return []
        
        # Common OBD-II codes
        possible_codes = [
            "P0171",  # System Too Lean
            "P0300",  # Random Misfire
            "P0420",  # Catalyst System Efficiency Below Threshold
            "P0128",  # Coolant Thermostat
            "P0455",  # EVAP System Leak Detected
            "P0442",  # EVAP System Leak Small
            "P0401",  # EGR Flow Insufficient
        ]
        
        # Return 1-2 random codes
        num_codes = random.randint(1, 2)
        return random.sample(possible_codes, num_codes)
    
    @staticmethod
    def generate_telemetry_stream(vehicle_id: str) -> Dict:
        """Generate real-time telemetry data (simulates streaming data)"""
        return {
            "vehicle_id": vehicle_id,
            "timestamp": datetime.now().isoformat(),
            "engine_temp": round(random.uniform(85.0, 110.0), 2),
            "oil_pressure": round(random.uniform(25.0, 65.0), 2),
            "battery_voltage": round(random.uniform(12.0, 14.5), 2),
            "tire_pressure": {
                "front_left": round(random.uniform(28.0, 35.0), 1),
                "front_right": round(random.uniform(28.0, 35.0), 1),
                "rear_left": round(random.uniform(28.0, 35.0), 1),
                "rear_right": round(random.uniform(28.0, 35.0), 1)
            },
            "fuel_level": round(random.uniform(10.0, 95.0), 1),
            "speed": round(random.uniform(0.0, 80.0), 1),
            "rpm": round(random.uniform(800.0, 4000.0), 0),
            "error_codes": [] if random.random() > 0.1 else [f"P{random.randint(100, 999)}"]
        }
