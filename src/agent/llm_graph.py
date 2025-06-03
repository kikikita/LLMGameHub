# src/agent/llm_graph.py

import logging
from langgraph.graph import StateGraph, END
from agent.tools import (
    generate_story_frame,
    generate_scene,
    generate_scene_image,
    update_state_with_choice,
    check_ending,
)
import logging
from agent.state import get_user_state
import uuid

logger = logging.getLogger(__name__)

# Определяем тип состояния, передаваемого между узлами графа
from dataclasses import dataclass, field
from typing import Optional, Dict, Any


@dataclass
class GraphState:
    user_hash: Optional[str] = None
    step: Optional[str] = None
    setting: Optional[str] = None
    character: Optional[Dict[str, Any]] = None
    genre: Optional[str] = None
    choice_text: Optional[str] = None
    scene: Optional[Dict[str, Any]] = None
    ending: Optional[Dict[str, Any]] = None

# ──────────────────────────────────────────────
# NODE: ROUTER (определяет ветку по типу шага)
# ──────────────────────────────────────────────
async def node_entry(state: GraphState) -> GraphState:
    logger.debug(f"[Graph] Entry state: {state}")
    return state

def route_step(state: GraphState) -> str:
    step = state.step
    logger.debug(f"[Graph] Routing step: {step}, state: {state}")
    if step == "start":
        return "init_game"
    elif step == "choose":
        return "player_step"
    elif step is None:
        # Явно логируем и возвращаем init_game (или другой дефолт)
        logging.warning("route_step получил state без ключа 'step', возвращаю 'init_game' по умолчанию.")
        return "init_game"
    else:
        raise ValueError(f"Unknown step: {step}")

# ──────────────────────────────────────────────
# NODE: ИНИЦИАЛИЗАЦИЯ ИГРЫ
# ──────────────────────────────────────────────
async def node_init_game(state: GraphState) -> GraphState:
    logger.debug(f"[Graph] node_init_game received state: {state}")
    user_hash = state.user_hash
    setting = state.setting
    character = state.character
    genre = state.genre
    logger.info(f"[Graph] Init game for user: {user_hash}")

    # Генерируем каркас истории (Story Frame)
    await generate_story_frame.ainvoke({
        "user_hash": user_hash,
        "setting": setting,
        "character": character,
        "genre": genre,
    })

    # Генерируем первую сцену
    first_scene = await generate_scene.ainvoke({
        "user_hash": user_hash,
        "last_choice": "start",
    })

    # Генерируем ассет для первой сцены (prefetch image)
    await generate_scene_image.ainvoke({
        "user_hash": user_hash,
        "scene_id": first_scene["scene_id"],
        "prompt": first_scene["description"],
    })

    # Запоминаем сцену в state для runner/UI
    state.scene = first_scene
    return state

# ──────────────────────────────────────────────
# NODE: ОБРАБОТКА ХОДА ИГРОКА
# ──────────────────────────────────────────────
async def node_player_step(state: GraphState) -> GraphState:
    logger.debug(f"[Graph] node_player_step received state: {state}")
    user_hash = state.user_hash
    choice_text = state.choice_text

    user_state = get_user_state(user_hash)
    scene_id = user_state.current_scene_id
    logger.info(f"[Graph] Player step for {user_hash}, choice: {choice_text}, scene: {scene_id}")

    if choice_text is not None:
        # 1. Сохраняем выбор пользователя в state
        await update_state_with_choice.ainvoke({
            "user_hash": user_hash,
            "scene_id": scene_id,
            "choice_text": choice_text,
        })
    else:
        logger.warning("[Graph] player_step called without choice_text")

    # 2. Проверяем, достигнута ли концовка
    ending = await check_ending.ainvoke({"user_hash": user_hash})
    state.ending = ending

    # 3. Если концовка не достигнута, генерируем следующую сцену и ассеты
    if not ending.get("ending_reached", False):
        next_scene = await generate_scene.ainvoke({
            "user_hash": user_hash,
            "last_choice": choice_text,
        })
        await generate_scene_image.ainvoke({
            "user_hash": user_hash,
            "scene_id": next_scene["scene_id"],
            "prompt": next_scene["description"],
        })
        state.scene = next_scene

    return state

def route_ending(state: GraphState) -> str:
    ending = state.ending or {}
    logger.debug(f"[Graph] route_ending check: {ending}")
    if ending.get("ending_reached", False):
        return "game_over"
    else:
        return "player_step"

# ──────────────────────────────────────────────
# NODE: ЗАВЕРШЕНИЕ ИГРЫ (END)
# ──────────────────────────────────────────────
async def node_game_over(state: GraphState) -> GraphState:
    logger.info(f"[Graph] Game over for user: {state.user_hash}")
    logger.debug(f"[Graph] node_game_over state: {state}")
    return state

# ──────────────────────────────────────────────
# GRAPH CONSTRUCTION
# ──────────────────────────────────────────────
def build_llm_game_graph():
    graph = StateGraph(GraphState)

    # 1. Все узлы графа
    graph.add_node("entry", node_entry)
    graph.add_node("init_game", node_init_game)
    graph.add_node("player_step", node_player_step)
    graph.add_node("game_over", node_game_over)

    # 2. Объявляем стартовый узел
    graph.set_entry_point("entry")

    # 3. Ветвление из router
    graph.add_conditional_edges(
        "entry", route_step,
        {
            "init_game": "init_game",
            "player_step": "player_step"
        }
    )

    # После инициализации завершаем шаг, чтобы пользователь увидел первую сцену
    graph.add_edge("init_game", END)

    # Ветвление после каждого шага игрока: если ending — завершаем, иначе цикл
    graph.add_conditional_edges(
        "player_step", route_ending,
        {
            "game_over": "game_over",
            "player_step": "player_step"
        }
    )

    # Завершающий узел
    graph.add_edge("game_over", END)

    return graph.compile()


llm_game_graph = build_llm_game_graph()
