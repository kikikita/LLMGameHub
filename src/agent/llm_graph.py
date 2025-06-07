"""LangGraph setup for the interactive fiction agent."""

import logging
from dataclasses import dataclass
from typing import Any, Dict, Optional
import asyncio
from langgraph.graph import END, StateGraph
from agent.image_agent import generate_image_prompt

from agent.tools import (
    check_ending,
    generate_scene,
    generate_scene_image,
    generate_story_frame,
    update_state_with_choice,
)
from agent.state import get_user_state
from audio.audio_generator import change_music_tone
logger = logging.getLogger(__name__)


@dataclass
class GraphState:
    """Mutable state passed between graph nodes."""

    user_hash: Optional[str] = None
    step: Optional[str] = None
    setting: Optional[str] = None
    character: Optional[Dict[str, Any]] = None
    genre: Optional[str] = None
    choice_text: Optional[str] = None
    scene: Optional[Dict[str, Any]] = None
    ending: Optional[Dict[str, Any]] = None


async def node_entry(state: GraphState) -> GraphState:
    logger.debug("[Graph] entry state: %s", state)
    return state


def route_step(state: GraphState) -> str:
    if state.step == "start":
        return "init_game"
    if state.step == "choose":
        return "player_step"
    logger.warning("route_step received unknown step '%s'", state.step)
    return "init_game"


async def node_init_game(state: GraphState) -> GraphState:
    logger.debug("[Graph] node_init_game state: %s", state)
    await generate_story_frame.ainvoke(
        {
            "user_hash": state.user_hash,
            "setting": state.setting,
            "character": state.character,
            "genre": state.genre,
        }
    )
    first_scene = await generate_scene.ainvoke(
        {"user_hash": state.user_hash, "last_choice": "start"}
    )
    change_scene = await generate_image_prompt(first_scene["description"], state.user_hash)
    logger.info(f"Change scene: {change_scene}")
    await generate_scene_image.ainvoke(
        {
            "user_hash": state.user_hash,
            "scene_id": first_scene["scene_id"],
            "change_scene": change_scene,
        }
    )
    state.scene = first_scene
    return state


async def node_player_step(state: GraphState) -> GraphState:
    logger.debug("[Graph] node_player_step state: %s", state)
    user_state = get_user_state(state.user_hash)
    scene_id = user_state.current_scene_id
    if state.choice_text:
        await update_state_with_choice.ainvoke(
            {
                "user_hash": state.user_hash,
                "scene_id": scene_id,
                "choice_text": state.choice_text,
            }
        )
    ending = await check_ending.ainvoke({"user_hash": state.user_hash})
    state.ending = ending
    if not ending.get("ending_reached", False):
        next_scene = await generate_scene.ainvoke(
            {
                "user_hash": state.user_hash,
                "last_choice": state.choice_text,
            }
        )
        change_scene = await generate_image_prompt(next_scene["description"], state.user_hash)
        image_task = generate_scene_image.ainvoke(
            {
                "user_hash": state.user_hash,
                "scene_id": next_scene["scene_id"],
                "current_image": user_state.assets[scene_id],
                "change_scene": change_scene,
            }
        )
        music_task = change_music_tone(state.user_hash, next_scene["music"])
        await asyncio.gather(image_task, music_task)
        state.scene = next_scene
    return state


def route_ending(state: GraphState) -> str:
    return "game_over" if state.ending.get("ending_reached") else "continue"


async def node_game_over(state: GraphState) -> GraphState:
    logger.info("[Graph] Game over for user %s", state.user_hash)
    return state


def build_llm_game_graph() -> StateGraph:
    graph = StateGraph(GraphState)
    graph.add_node("entry", node_entry)
    graph.add_node("init_game", node_init_game)
    graph.add_node("player_step", node_player_step)
    graph.add_node("game_over", node_game_over)

    graph.set_entry_point("entry")
    graph.add_conditional_edges(
        "entry",
        route_step,
        {"init_game": "init_game", "player_step": "player_step"},
    )
    graph.add_edge("init_game", END)
    graph.add_conditional_edges(
        "player_step",
        route_ending,
        {"game_over": "game_over", "continue": END},
    )
    graph.add_edge("game_over", END)
    return graph.compile()


llm_game_graph = build_llm_game_graph()
