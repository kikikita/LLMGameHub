"""Simple in-memory user state storage."""

from typing import Dict
import asyncio

from agent.models import UserState

_USER_STATE: Dict[str, UserState] = {}
_STATE_LOCKS: Dict[str, asyncio.Lock] = {}
_GLOBAL_LOCK = asyncio.Lock()


async def _get_lock(user_hash: str) -> asyncio.Lock:
    async with _GLOBAL_LOCK:
        if user_hash not in _STATE_LOCKS:
            _STATE_LOCKS[user_hash] = asyncio.Lock()
        return _STATE_LOCKS[user_hash]


async def get_user_state(user_hash: str) -> UserState:
    """Return user state for the given id, creating it if necessary."""
    lock = await _get_lock(user_hash)
    async with lock:
        if user_hash not in _USER_STATE:
            _USER_STATE[user_hash] = UserState()
        return _USER_STATE[user_hash]


async def set_user_state(user_hash: str, state: UserState) -> None:
    """Persist updated user state."""
    lock = await _get_lock(user_hash)
    async with lock:
        _USER_STATE[user_hash] = state


async def reset_user_state(user_hash: str) -> None:
    """Reset stored state for a user."""
    lock = await _get_lock(user_hash)
    async with lock:
        _USER_STATE[user_hash] = UserState()
