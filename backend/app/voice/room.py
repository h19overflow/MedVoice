"""
Daily Room Management

Creates temporary Daily.co rooms for WebRTC sessions.
"""

import time

import aiohttp

from backend.app.config import get_settings


async def create_daily_room(expiry_seconds: int = 3600) -> str:
    """
    Create a temporary Daily.co room.

    Args:
        expiry_seconds: Room expiration time in seconds.

    Returns:
        Room URL string.

    Raises:
        ValueError: If DAILY_API_KEY is not configured.
        RuntimeError: If room creation fails.
    """
    settings = get_settings()
    if not settings.daily_api_key:
        raise ValueError("DAILY_API_KEY not set")

    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://api.daily.co/v1/rooms",
            headers={
                "Authorization": f"Bearer {settings.daily_api_key}",
                "Content-Type": "application/json",
            },
            json={"properties": {"exp": int(time.time()) + expiry_seconds}},
        ) as response:
            if response.status != 200:
                error = await response.text()
                raise RuntimeError(f"Failed to create room: {error}")
            room = await response.json()
            return room["url"]
