"""
AI Engine Client for ResQ-AI Backend
Handles communication with the AI engine service
"""

import asyncio
import httpx
import json
import os
import importlib.util
import traceback
from typing import Dict, Any, Optional
from loguru import logger

class AIClient:
    def __init__(self, base_url: Optional[str] = None):
        self.base_url = base_url or os.getenv("AI_ENGINE_URL", "http://localhost:5000")
        self.local_model_path = os.getenv("AI_MODEL_PATH", "").strip()
        self.local_model = None
        self.client: Optional[httpx.AsyncClient] = None
        self.connected = False

        self.endpoints = {
            "process_video": os.getenv("AI_PROCESS_VIDEO_PATH", "/api/detect"),
            "analyze_message": os.getenv("AI_ANALYZE_MESSAGE_PATH", "/api/analyze"),
            "analyze_alert": os.getenv("AI_ANALYZE_ALERT_PATH", "/api/alert-insights"),
            "status": os.getenv("AI_STATUS_PATH", "/api/status"),
        }

    def _load_local_model(self):
        """Load local AI model module from AI_MODEL_PATH"""
        if not self.local_model_path:
            return None

        try:
            if not os.path.isfile(self.local_model_path):
                raise FileNotFoundError(f"Local model file not found: {self.local_model_path}")

            spec = importlib.util.spec_from_file_location("custom_ai_model", self.local_model_path)
            if spec is None or spec.loader is None:
                raise ImportError(f"Invalid module spec for path: {self.local_model_path}")

            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Sanity check: required methods
            required = ["process_video", "analyze_message", "analyze_alert", "status"]
            for method in required:
                if not hasattr(module, method):
                    raise AttributeError(f"Custom model is missing required method: {method}")

            logger.info(f"Loaded local AI model from {self.local_model_path}")
            return module

        except Exception as e:
            logger.error(f"Failed to load local AI model: {e}\n{traceback.format_exc()}")
            return None

    async def connect(self):
        """Initialize connection to either local or remote AI engine"""
        if self.local_model_path:
            self.local_model = self._load_local_model()
            if self.local_model:
                self.connected = True
                logger.info("Connected to local AI model")
                return
            else:
                logger.warning("Local AI model path configured but failed to load, falling back to remote AI engine")

        try:
            self.client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=30.0
            )
            # quick health check
            resp = await self.client.get(self.endpoints.get("status", "/api/status"))
            resp.raise_for_status()
            self.connected = True
            logger.info(f"Connected to AI Engine at {self.base_url}")
        except Exception as e:
            logger.error(f"Failed to connect to AI Engine: {e}")
            self.connected = False

    async def disconnect(self):
        """Close HTTP client connection"""
        if self.client:
            await self.client.aclose()
            self.connected = False
            logger.info("Disconnected from AI Engine")

    async def _invoke_local(self, method_name: str, **kwargs):
        """Call local model method (sync or async)"""
        if not self.local_model:
            return {"error": "local model not loaded"}

        fn = getattr(self.local_model, method_name, None)
        if not fn:
            return {"error": f"local model has no method {method_name}"}

        try:
            result = fn(**kwargs)
            if asyncio.iscoroutine(result):
                result = await result
            return result
        except Exception as e:
            logger.error(f"Local model execution error ({method_name}): {e}\n{traceback.format_exc()}")
            return {"error": str(e)}

    async def process_video(self, video_url: str, drone_id: str) -> Dict[str, Any]:
        """Process video feed for survivor detection"""
        if self.local_model:
            return await self._invoke_local("process_video", video_url=video_url, drone_id=drone_id)

        if not self.connected or not self.client:
            return {"error": "AI Engine not connected"}

        try:
            payload = {
                "video_url": video_url,
                "drone_id": drone_id,
                "timestamp": asyncio.get_event_loop().time()
            }

            response = await self.client.post(self.endpoints.get("process_video", "/api/detect"), json=payload)
            response.raise_for_status()

            result = response.json()
            logger.info(f"Video processing completed for drone {drone_id}")
            return result

        except httpx.HTTPError as e:
            logger.error(f"AI Engine request failed: {e}")
            return {"error": str(e)}
        except Exception as e:
            logger.error(f"Video processing error: {e}")
            return {"error": str(e)}

    async def analyze_message(self, message: str) -> Dict[str, Any]:
        """Analyze emergency message with NLP"""
        if self.local_model:
            return await self._invoke_local("analyze_message", message=message)

        if not self.connected or not self.client:
            return {"error": "AI Engine not connected"}

        try:
            payload = {
                "message": message,
                "timestamp": asyncio.get_event_loop().time()
            }

            response = await self.client.post(self.endpoints.get("analyze_message", "/api/analyze"), json=payload)
            response.raise_for_status()

            result = response.json()
            logger.info("Message analysis completed")
            return result

        except httpx.HTTPError as e:
            logger.error(f"AI Engine request failed: {e}")
            return {"error": str(e)}
        except Exception as e:
            logger.error(f"Message analysis error: {e}")
            return {"error": str(e)}

    async def analyze_alert(self, alert_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze emergency alert for additional insights"""
        if self.local_model:
            return await self._invoke_local("analyze_alert", alert_data=alert_data)

        if not self.connected or not self.client:
            return {"error": "AI Engine not connected"}

        try:
            response = await self.client.post(self.endpoints.get("analyze_alert", "/api/alert-insights"), json=alert_data)
            response.raise_for_status()

            result = response.json()
            logger.info("Alert analysis completed")
            return result

        except httpx.HTTPError as e:
            logger.error(f"AI Engine request failed: {e}")
            return {"error": str(e)}
        except Exception as e:
            logger.error(f"Alert analysis error: {e}")
            return {"error": str(e)}

    async def get_model_status(self) -> Dict[str, Any]:
        """Get AI model status and health"""
        if self.local_model:
            status_result = await self._invoke_local("status")
            if isinstance(status_result, dict) and status_result.get("status"):
                return status_result
            return {"status": "healthy", "detail": "local model loaded"}

        if not self.connected or not self.client:
            return {"status": "disconnected"}

        try:
            response = await self.client.get(self.endpoints.get("status", "/api/status"))
            response.raise_for_status()

            return response.json()

        except httpx.HTTPError as e:
            logger.error(f"Status check failed: {e}")
            return {"status": "error", "error": str(e)}
        except Exception as e:
            logger.error(f"Status check error: {e}")
            return {"status": "error", "error": str(e)}

    async def health_check(self) -> bool:
        """Perform health check on AI engine"""
        status = await self.get_model_status()
        return status.get("status") == "healthy"

# Create global instance
ai_client = AIClient()