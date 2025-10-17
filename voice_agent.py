"""Voice agent integration layer for outbound/inbound calls.

Provides human-like conversational outreach leveraging Twilio when available
and falls back to on-device speech synthesis for offline demos.
"""

from __future__ import annotations

import asyncio
import os
import uuid
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel, Field

try:  # Optional Twilio dependency
    from twilio.rest import Client
    from twilio.twiml.voice_response import Gather, VoiceResponse

    HAS_TWILIO = True
except Exception:  # pragma: no cover - gracefully degrade when Twilio missing
    Client = None
    Gather = None
    VoiceResponse = None
    HAS_TWILIO = False

try:  # Optional offline TTS engine (Windows/Linux friendly)
    import pyttsx3

    HAS_PYTTSX3 = True
except Exception:  # pragma: no cover - pyttsx3 not mandatory
    pyttsx3 = None
    HAS_PYTTSX3 = False


@dataclass
class VoiceIntentEvent:
    """Structured callback for intents captured during calls."""

    call_id: str
    customer_id: Optional[str]
    intent: str
    transcript: str
    digits: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class VoiceCallScript:
    """Metadata for an active or simulated voice call."""

    call_id: str
    customer_id: str
    customer_name: str
    phone: str
    message: str
    prompt: str
    followup_message: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    twilio_sid: Optional[str] = None


class VoiceAgent:
    """Voice engagement assistant with optional telephony provider integration."""

    def __init__(
        self,
        *,
        ueba=None,
        base_url: Optional[str] = None,
        caller_id: Optional[str] = None,
        default_voice: str = "Polly.Joanna",
        language: str = "en-US",
        intent_callback: Optional[Callable[[VoiceIntentEvent], None]] = None,
    ) -> None:
        self.ueba = ueba
        self.base_url = base_url or os.getenv("VOICE_WEBHOOK_BASE_URL")
        self.language = language
        self.caller_id = caller_id or os.getenv("TWILIO_CALLER_ID")
        self.default_voice = default_voice
        self.intent_callback = intent_callback

        self.account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.twilio_enabled = bool(
            HAS_TWILIO and self.account_sid and self.auth_token and self.caller_id and self.base_url
        )
        self.client: Any = None
        if self.twilio_enabled and Client:
            self.client = Client(self.account_sid, self.auth_token)

        self.outgoing_audio_dir = Path(os.getenv("VOICE_AUDIO_DIR", "voice_calls"))
        self.outgoing_audio_dir.mkdir(parents=True, exist_ok=True)

        self._scripts: Dict[str, VoiceCallScript] = {}
        self._events: List[Dict[str, Any]] = []
        self._lock = asyncio.Lock()

    # ------------------------------------------------------------------ helpers
    def _log_event(self, payload: Dict[str, Any]) -> None:
        payload["timestamp"] = payload.get("timestamp") or time.monotonic()
        self._events.append(payload)
        if self.ueba:
            try:
                self.ueba.log_activity("VoiceAgent", payload.get("action", "event"), "voice")
            except Exception:
                pass

    def _humanize_prompt(self, script: VoiceCallScript) -> str:
        base = script.message.strip()
        if not base.endswith("."):
            base += "."
        return (
            f"Hello {script.customer_name}, this is the AutoPulse predictive maintenance desk calling. "
            f"{base} {script.prompt}"
        )

    # ------------------------------------------------------------------ public API
    async def place_outbound_call(
        self,
        *,
        customer: Dict[str, Any],
        vehicle: Dict[str, Any],
        prediction: Dict[str, Any],
        message: str,
    ) -> VoiceCallScript:
        call_id = str(uuid.uuid4())
        script = VoiceCallScript(
            call_id=call_id,
            customer_id=customer.get("id", ""),
            customer_name=customer.get("name", "Customer"),
            phone=customer.get("phone", ""),
            message=message,
            prompt="Press 1 to confirm the recommended service or press 2 to request a human advisor.",
            followup_message="We'll keep monitoring your vehicle. Drive safe!",
            metadata={
                "prediction_id": prediction.get("id"),
                "priority": prediction.get("priority"),
                "vehicle_id": prediction.get("vehicle_id"),
                "vehicle_model": vehicle.get("model"),
                "service_type": prediction.get("predicted_issue", "AI Recommended Maintenance"),
            },
        )

        async with self._lock:
            self._scripts[call_id] = script

        if not script.phone:
            self._log_event({
                "action": "missing_phone",
                "call_id": call_id,
                "customer": script.customer_name,
                "metadata": script.metadata,
            })
            return script

        if self.twilio_enabled:
            await asyncio.to_thread(self._initiate_twilio_call, script)
        else:
            await self._synthesize_offline_audio(script)

        self._log_event({
            "action": "outbound_initiated",
            "call_id": call_id,
            "customer": script.customer_name,
            "phone": script.phone,
            "provider": "twilio" if self.twilio_enabled else "offline",
            "metadata": script.metadata,
        })

        return script

    def get_script(self, call_id: str) -> Optional[VoiceCallScript]:
        return self._scripts.get(call_id)

    def list_events(self) -> List[Dict[str, Any]]:
        return self._events[-200:]

    # ------------------------------------------------------------------ provider ops
    def _initiate_twilio_call(self, script: VoiceCallScript) -> None:
        if not self.client or not self.base_url:
            raise RuntimeError("Twilio client not configured")
        call = self.client.calls.create(
            to=script.phone,
            from_=self.caller_id,
            url=f"{self.base_url}/api/voice/twiml/{script.call_id}",
            status_callback=f"{self.base_url}/api/voice/status",
            status_callback_event=["initiated", "ringing", "answered", "completed"],
        )
        script.twilio_sid = call.sid
        self._scripts[script.call_id] = script

    async def _synthesize_offline_audio(self, script: VoiceCallScript) -> None:
        """Generate a local audio file to simulate the call when Twilio is unavailable."""
        audio_path = self.outgoing_audio_dir / f"{script.call_id}.mp3"
        narration = self._humanize_prompt(script)
        if HAS_PYTTSX3:
            def _render() -> None:
                engine = pyttsx3.init()
                engine.setProperty("rate", 180)
                engine.save_to_file(narration, str(audio_path))
                engine.runAndWait()

            await asyncio.to_thread(_render)
        else:
            audio_path.write_text(narration, encoding="utf-8")

        self._log_event({
            "action": "offline_audio_rendered",
            "path": str(audio_path),
            "call_id": script.call_id,
        })

    # ------------------------------------------------------------------ TwiML generation
    def generate_twiml(self, script: VoiceCallScript) -> str:
        if not HAS_TWILIO:
            raise HTTPException(status_code=503, detail="Twilio library not available on server")

        response = VoiceResponse()
        response.say(self._humanize_prompt(script), voice=self.default_voice, language=self.language)

        gather = Gather(
            input="speech dtmf",
            timeout=6,
            speech_timeout="auto",
            action=f"/api/voice/gather/{script.call_id}",
            method="POST",
            language=self.language,
            num_digits=1,
        )
        gather.say(pathos := script.prompt, voice=self.default_voice, language=self.language)
        response.append(gather)
        response.say(script.followup_message, voice=self.default_voice, language=self.language)
        response.hangup()
        return str(response)

    async def handle_gather(self, call_id: str, payload: Dict[str, Any]) -> Response:
        script = self.get_script(call_id)
        if not script:
            raise HTTPException(status_code=404, detail="Call not found")

        digits = payload.get("Digits")
        transcript = payload.get("SpeechResult", "").strip()
        intent = "unknown"
        if digits == "1" or "confirm" in transcript.lower():
            intent = "confirm_service"
        elif digits == "2" or "human" in transcript.lower():
            intent = "escalate_human"

        event = VoiceIntentEvent(
            call_id=call_id,
            customer_id=script.customer_id,
            intent=intent,
            transcript=transcript,
            digits=digits,
            metadata=script.metadata,
        )
        if self.intent_callback:
            try:
                self.intent_callback(event)
            except Exception as exc:  # pragma: no cover - downstream handler failure
                self._log_event({
                    "action": "intent_callback_error",
                    "call_id": call_id,
                    "error": str(exc),
                })

        self._log_event({
            "action": "intent_detected",
            "call_id": call_id,
            "intent": intent,
            "digits": digits,
            "transcript": transcript,
            "metadata": script.metadata,
        })

        if HAS_TWILIO:
            followup = VoiceResponse()
            if intent == "confirm_service":
                followup.say(
                    "Thanks for confirming. We'll lock in the appointment and send you the details via SMS.",
                    voice=self.default_voice,
                    language=self.language,
                )
            elif intent == "escalate_human":
                followup.say(
                    "A service specialist will call you shortly. Thank you for your patience.",
                    voice=self.default_voice,
                    language=self.language,
                )
            else:
                followup.say(
                    "Thanks for the update. We'll continue monitoring your vehicle.",
                    voice=self.default_voice,
                    language=self.language,
                )
            followup.hangup()
            return Response(content=str(followup), media_type="application/xml")

        return JSONResponse({"status": "captured", "intent": intent})

    def handle_status_callback(self, payload: Dict[str, Any]) -> None:
        call_sid = payload.get("CallSid")
        call_id = None
        for sid_call_id, script in self._scripts.items():
            if script.twilio_sid == call_sid:
                call_id = sid_call_id
                break
        self._log_event({
            "action": "status_update",
            "call_sid": call_sid,
            "call_id": call_id,
            "status": payload.get("CallStatus"),
        })


# ---------------------------------------------------------------------------
# FastAPI router factory



from pydantic import BaseModel, Field

class VoiceCallRequest(BaseModel):
    customer_id: str
    customer_name: str
    phone: str
    message: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

def create_voice_router(agent_getter: Callable[[], Optional[VoiceAgent]]) -> APIRouter:
    router = APIRouter(prefix="/api/voice", tags=["voice"])

    @router.post("/outbound")
    async def outbound_call(request: VoiceCallRequest):
        agent = agent_getter()
        if not agent:
            raise HTTPException(status_code=503, detail="Voice agent not ready")
        customer = {"id": request.customer_id, "name": request.customer_name, "phone": request.phone}
        prediction_stub = {"id": request.metadata.get("prediction_id"), "priority": request.metadata.get("priority", "medium"), "vehicle_id": request.metadata.get("vehicle_id")}
        vehicle_stub = {"model": request.metadata.get("vehicle_model", "Vehicle")}
        script = await agent.place_outbound_call(customer=customer, vehicle=vehicle_stub, prediction=prediction_stub, message=request.message)
        return {"call_id": script.call_id, "provider": "twilio" if agent.twilio_enabled else "offline"}

    @router.api_route("/twiml/{call_id}", methods=["GET", "POST"])
    async def outbound_twiml(call_id: str):
        agent = agent_getter()
        if not agent:
            raise HTTPException(status_code=503, detail="Voice agent not ready")
        script = agent.get_script(call_id)
        if not script:
            raise HTTPException(status_code=404, detail="Call script not found")
        return Response(content=agent.generate_twiml(script), media_type="application/xml")

    @router.post("/gather/{call_id}")
    async def gather_result(call_id: str, request: Request):
        agent = agent_getter()
        if not agent:
            raise HTTPException(status_code=503, detail="Voice agent not ready")
        form = await request.form()
        return await agent.handle_gather(call_id, dict(form))

    @router.post("/status")
    async def status_callback(request: Request):
        agent = agent_getter()
        if not agent:
            raise HTTPException(status_code=503, detail="Voice agent not ready")
        form = await request.form()
        agent.handle_status_callback(dict(form))
        return {"status": "ok"}

    @router.get("/events")
    async def list_events():
        agent = agent_getter()
        if not agent:
            raise HTTPException(status_code=503, detail="Voice agent not ready")
        return {"events": agent.list_events()}

    return router
