"""Entry point for executing a graph step."""

import logging
from dataclasses import asdict
from typing import Dict, Optional

from agent.llm_graph import GraphState, llm_game_graph
from agent.models import UserState
from agent.state import get_user_state

logger = logging.getLogger(__name__)


async def process_step(
    user_hash: str,
    step: str,
    setting: Optional[str] = None,
    character: Optional[dict] = None,
    genre: Optional[str] = None,
    choice_text: Optional[str] = None,
) -> Dict:
    """Run one interaction step through the graph."""
    logger.info("[Runner] Step %s for user %s", step, user_hash)

    graph_state = GraphState(user_hash=user_hash, step=step)
    if step == "start":
        assert setting and character and genre, "Missing start parameters"
        graph_state.setting = setting
        graph_state.character = character
        graph_state.genre = genre
    elif step == "choose":
        assert choice_text, "choice_text is required"
        graph_state.choice_text = choice_text

    final_state = await llm_game_graph.ainvoke(asdict(graph_state))

    user_state: UserState = get_user_state(user_hash)
    response: Dict = {}

    ending = final_state.get("ending")
    if ending and ending.get("ending_reached"):
        response["ending"] = ending["ending"]
        response["game_over"] = True
    else:
        if (
            user_state.current_scene_id
            and user_state.current_scene_id in user_state.scenes
        ):
            current_scene = user_state.scenes[
                user_state.current_scene_id
            ].dict()
        else:
            current_scene = final_state.get("scene")
        response["scene"] = current_scene
        response["game_over"] = False

    return response
