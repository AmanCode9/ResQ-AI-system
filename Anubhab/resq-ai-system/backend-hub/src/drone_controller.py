"""
Drone Controller Module
Handles drone telemetry, commands, and mission management
"""

import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json
from dataclasses import dataclass
from loguru import logger

@dataclass
class Drone:
    """Drone data structure"""
    drone_id: str
    model: str
    capabilities: List[str]  # ["video", "thermal", "gps", "communication"]
    max_altitude: float
    max_speed: float
    battery_capacity: float
    status: str  # "active", "standby", "maintenance", "emergency"
    current_mission: Optional[str] = None
    last_telemetry: Optional[Dict[str, Any]] = None
    last_seen: Optional[datetime] = None

class DroneController:
    """Manages drone fleet operations"""

    def __init__(self):
        self.drones: Dict[str, Drone] = {}
        self.mission_history: List[Dict[str, Any]] = []
        self.telemetry_buffer: Dict[str, List[Dict[str, Any]]] = {}

    def register_drone(self, drone_id: str, model: str, capabilities: List[str]):
        """Register a new drone in the system"""
        if drone_id in self.drones:
            logger.warning(f"Drone {drone_id} already registered")
            return False

        drone = Drone(
            drone_id=drone_id,
            model=model,
            capabilities=capabilities,
            max_altitude=100.0,  # meters
            max_speed=20.0,      # m/s
            battery_capacity=5000.0,  # mAh
            status="standby"
        )

        self.drones[drone_id] = drone
        self.telemetry_buffer[drone_id] = []
        logger.info(f"Drone {drone_id} registered successfully")
        return True

    def update_telemetry(self, drone_id: str, telemetry: Dict[str, Any]) -> bool:
        """Update drone telemetry data"""
        if drone_id not in self.drones:
            logger.error(f"Unknown drone {drone_id}")
            return False

        drone = self.drones[drone_id]
        drone.last_telemetry = telemetry
        drone.last_seen = datetime.now()

        # Update status based on telemetry
        battery_level = telemetry.get("battery_level", 100)
        if battery_level < 10:
            drone.status = "emergency"
        elif battery_level < 20:
            drone.status = "low_battery"
        else:
            drone.status = "active"

        # Buffer telemetry for analysis
        self.telemetry_buffer[drone_id].append({
            **telemetry,
            "timestamp": datetime.now().isoformat()
        })

        # Keep only last 100 readings
        if len(self.telemetry_buffer[drone_id]) > 100:
            self.telemetry_buffer[drone_id] = self.telemetry_buffer[drone_id][-100:]

        logger.debug(f"Telemetry updated for drone {drone_id}")
        return True

    def get_drone_status(self, drone_id: str) -> Optional[Dict[str, Any]]:
        """Get current status of a drone"""
        if drone_id not in self.drones:
            return None

        drone = self.drones[drone_id]
        return {
            "drone_id": drone.drone_id,
            "model": drone.model,
            "capabilities": drone.capabilities,
            "status": drone.status,
            "current_mission": drone.current_mission,
            "last_seen": drone.last_seen.isoformat() if drone.last_seen else None,
            "telemetry": drone.last_telemetry
        }

    def get_all_drones(self) -> List[Dict[str, Any]]:
        """Get status of all registered drones"""
        return [self.get_drone_status(drone_id) for drone_id in self.drones.keys()]

    def assign_mission(self, drone_id: str, mission_id: str, mission_type: str) -> bool:
        """Assign a mission to a drone"""
        if drone_id not in self.drones:
            logger.error(f"Unknown drone {drone_id}")
            return False

        drone = self.drones[drone_id]
        if drone.status not in ["active", "standby"]:
            logger.error(f"Drone {drone_id} not available for mission")
            return False

        drone.current_mission = mission_id
        drone.status = "busy"

        # Log mission assignment
        self.mission_history.append({
            "mission_id": mission_id,
            "drone_id": drone_id,
            "mission_type": mission_type,
            "assigned_at": datetime.now().isoformat(),
            "status": "assigned"
        })

        logger.info(f"Mission {mission_id} assigned to drone {drone_id}")
        return True

    def complete_mission(self, drone_id: str, mission_id: str, success: bool = True) -> bool:
        """Mark mission as completed"""
        if drone_id not in self.drones:
            return False

        drone = self.drones[drone_id]
        if drone.current_mission != mission_id:
            logger.error(f"Mission {mission_id} not assigned to drone {drone_id}")
            return False

        drone.current_mission = None
        drone.status = "active"

        # Update mission history
        for mission in self.mission_history:
            if mission["mission_id"] == mission_id:
                mission["completed_at"] = datetime.now().isoformat()
                mission["status"] = "completed" if success else "failed"
                break

        logger.info(f"Mission {mission_id} completed by drone {drone_id}")
        return True

    def send_command(self, drone_id: str, command: str, parameters: Dict[str, Any]) -> bool:
        """Send command to drone"""
        if drone_id not in self.drones:
            logger.error(f"Unknown drone {drone_id}")
            return False

        # In a real implementation, this would send commands via radio, API, or other communication
        logger.info(f"Sending command '{command}' to drone {drone_id} with params: {parameters}")

        # Simulate command execution
        asyncio.create_task(self._simulate_command_execution(drone_id, command, parameters))

        return True

    async def _simulate_command_execution(self, drone_id: str, command: str, parameters: Dict[str, Any]):
        """Simulate command execution (replace with actual drone communication)"""
        await asyncio.sleep(1)  # Simulate network delay

        # Log command execution
        logger.info(f"Command '{command}' executed on drone {drone_id}")

    def get_telemetry_history(self, drone_id: str, hours: int = 1) -> List[Dict[str, Any]]:
        """Get telemetry history for a drone"""
        if drone_id not in self.telemetry_buffer:
            return []

        cutoff_time = datetime.now() - timedelta(hours=hours)
        history = []

        for reading in self.telemetry_buffer[drone_id]:
            reading_time = datetime.fromisoformat(reading["timestamp"])
            if reading_time >= cutoff_time:
                history.append(reading)

        return history

    def get_mission_history(self, drone_id: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Get mission history"""
        if drone_id:
            history = [m for m in self.mission_history if m["drone_id"] == drone_id]
        else:
            history = self.mission_history

        return history[-limit:]  # Return most recent missions

    def check_drone_health(self, drone_id: str) -> Dict[str, Any]:
        """Perform health check on drone"""
        if drone_id not in self.drones:
            return {"status": "unknown", "error": "Drone not registered"}

        drone = self.drones[drone_id]

        health_status = {
            "drone_id": drone_id,
            "overall_status": "healthy",
            "checks": {}
        }

        # Check last seen
        if drone.last_seen:
            time_since_last_seen = datetime.now() - drone.last_seen
            if time_since_last_seen > timedelta(minutes=5):
                health_status["checks"]["connectivity"] = "warning"
                health_status["overall_status"] = "degraded"
            else:
                health_status["checks"]["connectivity"] = "healthy"
        else:
            health_status["checks"]["connectivity"] = "unknown"
            health_status["overall_status"] = "unknown"

        # Check battery
        if drone.last_telemetry:
            battery = drone.last_telemetry.get("battery_level", 100)
            if battery < 10:
                health_status["checks"]["battery"] = "critical"
                health_status["overall_status"] = "critical"
            elif battery < 20:
                health_status["checks"]["battery"] = "warning"
                if health_status["overall_status"] == "healthy":
                    health_status["overall_status"] = "warning"
            else:
                health_status["checks"]["battery"] = "healthy"
        else:
            health_status["checks"]["battery"] = "unknown"

        return health_status

# Global drone controller instance
drone_controller = DroneController()