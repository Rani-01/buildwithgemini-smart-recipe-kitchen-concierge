"""Minimal FastAPI proxy for a deployed A2A agent (Agent Runtime, agents-cli 1.1.0+).

The browser talks ONLY to this proxy (same origin, no CORS, no GCP creds in the
browser). The proxy authenticates with Application Default Credentials and
forwards chat to the deployed agent over the A2A protocol, returning replies as
structured parts the chat UI knows how to show:

  * {"kind": "text", "text": ...}  -> a normal chat bubble
  * {"kind": "a2ui", "data": ...}  -> one A2UI message (beginRendering /
    surfaceUpdate); static/index.html renders these as a card.
"""

import os
import uuid
from pathlib import Path

from dotenv import load_dotenv

# Load local .env if present
load_dotenv(Path(__file__).parent / ".env")
load_dotenv()

import google.auth
import google.auth.transport.requests
import httpx
from a2a.client import ClientConfig, create_client
from a2a.types import Message, Part, Role, SendMessageRequest
from a2a.utils.constants import (
    PROTOCOL_VERSION_1_0,
    VERSION_HEADER,
    TransportProtocol,
)
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

RESOURCE = os.environ["AGENT_ENGINE_RESOURCE_NAME"]
AGENT_DIRECTORY = os.environ.get("AGENT_DIRECTORY", "app")
LOCATION = RESOURCE.split("/locations/")[1].split("/")[0]

A2A_BASE = (
    f"https://{LOCATION}-aiplatform.googleapis.com/reasoningEngines/v1/"
    f"{RESOURCE}/api/a2a/{AGENT_DIRECTORY}"
)

_A2UI_MIME = "application/json+a2ui"

STATIC_DIR = Path(__file__).parent / "static"
app = FastAPI(title="Agent Chat Proxy")
app.mount("/chat-ui", StaticFiles(directory=str(STATIC_DIR), html=True), name="static")

_contexts: dict[str, str] = {}


def _auth_headers() -> dict[str, str]:
    credentials, _ = google.auth.default(
        scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )
    request = google.auth.transport.requests.Request()
    credentials.refresh(request)
    return {
        "Authorization": f"Bearer {credentials.token}",
        VERSION_HEADER: PROTOCOL_VERSION_1_0,
    }


def _extract_parts(parts) -> list[dict]:
    out: list[dict] = []
    for p in parts:
        text = getattr(p, "text", None)
        if text:
            out.append({"kind": "text", "text": text})
            continue

        raw = getattr(p, "raw", None)
        if raw is not None:
            data = getattr(raw, "data", None)
            mime = getattr(raw, "mime_type", None) or getattr(raw, "mimeType", None)
            if mime == _A2UI_MIME and data:
                out.append({"kind": "a2ui", "data": data})
            elif data:
                out.append({"kind": "text", "text": str(data)})
    return out


@app.post("/chat")
async def chat(req: Request):
    body = await req.json()
    message = body.get("message", "")
    user_id = body.get("user_id") or "web-user"
    parts: list[dict] = []

    req_headers = _auth_headers()
    async with httpx.AsyncClient(headers=req_headers, timeout=120) as http_client:
        config = ClientConfig(
            httpx_client=http_client,
            supported_protocol_bindings=[
                TransportProtocol.JSONRPC,
                TransportProtocol.HTTP_JSON,
            ],
        )
        try:
            a2a_client = await create_client(A2A_BASE, config)
        except Exception as exc:
            return JSONResponse(
                status_code=502,
                content={"error": f"Failed to connect to A2A agent: {exc}"},
            )

        msg = Message(
            message_id=str(uuid.uuid4()),
            role=Role.ROLE_USER,
            parts=[Part(text=message)],
            context_id=_contexts.get(user_id, ""),
        )

        try:
            async for chunk in a2a_client.send_message(SendMessageRequest(message=msg)):
                if chunk.HasField("artifact_update"):
                    if chunk.artifact_update.context_id:
                        _contexts[user_id] = chunk.artifact_update.context_id
                    parts.extend(_extract_parts(chunk.artifact_update.artifact.parts))
                elif chunk.HasField("task"):
                    if chunk.task.context_id:
                        _contexts[user_id] = chunk.task.context_id
                    for artifact in chunk.task.artifacts:
                        parts.extend(_extract_parts(artifact.parts))
                elif chunk.HasField("message"):
                    if chunk.message.context_id:
                        _contexts[user_id] = chunk.message.context_id
                    parts.extend(_extract_parts(chunk.message.parts))
        except Exception as exc:
            return JSONResponse(
                status_code=502,
                content={"error": f"Error during A2A message exchange: {exc}"},
            )

    return {"parts": parts}


@app.get("/")
async def root():
    return JSONResponse(
        content={
            "service": "agent-chat-proxy",
            "agent_directory": AGENT_DIRECTORY,
            "resource": RESOURCE,
            "ui_url": "/chat-ui/",
        }
    )
