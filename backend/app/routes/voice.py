"""
Voice Route

WebSocket endpoint for real-time voice interactions via Pipecat.
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from ..services.intake import get_session

router = APIRouter()


@router.websocket("/sessions/{session_id}/voice")
async def voice_websocket(websocket: WebSocket, session_id: str) -> None:
    """
    WebSocket endpoint for voice-based intake.

    This will be connected to the Pipecat pipeline for:
    - Receiving audio from the client
    - Processing through STT -> IntakeService -> TTS
    - Sending audio back to the client

    For MVP, we use Daily.co as the WebRTC transport,
    so this endpoint may be replaced with Daily.co room management.
    """
    service = get_session(session_id)
    if not service:
        await websocket.close(code=4004, reason="Session not found")
        return

    await websocket.accept()

    try:
        # TODO: Integrate with Pipecat pipeline
        # For now, this is a placeholder that echoes text messages

        # Send greeting
        greeting = service.get_greeting()
        await websocket.send_json({
            "type": "agent_message",
            "text": greeting,
            "state": service.state.value,
        })

        while True:
            # Receive message from client
            data = await websocket.receive_json()

            if data.get("type") == "user_message":
                # Process text message (transcribed on client or server)
                user_text = data.get("text", "")
                response = await service.process_message(user_text)

                await websocket.send_json({
                    "type": "agent_message",
                    "text": response,
                    "state": service.state.value,
                    "is_complete": service.is_complete(),
                })

                if service.is_complete():
                    # Send final results
                    await websocket.send_json({
                        "type": "intake_complete",
                        "data": service.get_intake_data().model_dump(mode="json"),
                    })

            elif data.get("type") == "audio_chunk":
                # TODO: Handle audio chunks through Pipecat
                pass

    except WebSocketDisconnect:
        # Client disconnected
        pass
    except Exception as e:
        await websocket.send_json({
            "type": "error",
            "message": str(e),
        })
        await websocket.close(code=1011, reason="Internal error")
