"""Simple in-memory user state storage."""

from typing import Dict

from agent.models import UserState

_USER_STATE: Dict[str, UserState] = {}


def get_user_state(user_hash: str) -> UserState:
    """Return user state for the given id, creating it if necessary."""
    if user_hash not in _USER_STATE:
        _USER_STATE[user_hash] = UserState()
    return _USER_STATE[user_hash]


def set_user_state(user_hash: str, state: UserState) -> None:
    """Persist updated user state."""
    _USER_STATE[user_hash] = state


def reset_user_state(user_hash: str) -> None:
    """Reset stored state for a user."""
    _USER_STATE[user_hash] = UserState()
