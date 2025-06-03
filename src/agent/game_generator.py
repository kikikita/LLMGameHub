"""
Фасад, который вызывает UI.

• start_game(...)  -> initial scene + state key
• next_turn(key, choice) -> scene / ending
"""

from __future__ import annotations
import uuid
from typing import Dict, Tuple

from agent.llm_graph import graph
from agent.state import GameState

# session_key -> GameState
_SESSIONS: Dict[str, GameState] = {}


def start_game(genre: str, pitch: str) -> Tuple[str, GameState]:
    key = str(uuid.uuid4())
    init_state: GameState = graph.invoke({"genre": genre, "pitch": pitch})
    _SESSIONS[key] = init_state
    return key, init_state


def next_turn(session_key: str, choice: str) -> GameState:
    if session_key not in _SESSIONS:
        raise ValueError("unknown session")
    state = _SESSIONS[session_key]
    new_state: GameState = graph.invoke(state, choice)
    _SESSIONS[session_key] = new_state
    return new_state
