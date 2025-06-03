from typing import Dict
from agent.models import UserState


_USER_STATE: Dict[str, UserState] = {}


def get_user_state(user_hash: str) -> UserState:
    """
    Получить или инициализировать состояние пользователя по user_hash/session_id.
    """
    if user_hash not in _USER_STATE:
        _USER_STATE[user_hash] = UserState()
    return _USER_STATE[user_hash]


def set_user_state(user_hash: str, state: UserState):
    """
    Сохранить состояние пользователя.
    """
    _USER_STATE[user_hash] = state


def reset_user_state(user_hash: str):
    """
    Сбросить состояние пользователя (например, при начале новой игры).
    """
    _USER_STATE[user_hash] = UserState()
