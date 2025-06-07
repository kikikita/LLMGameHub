"""Entry point for executing a graph step."""

import logging
from dataclasses import asdict
from typing import Dict, Optional
import uuid

from agent.image_agent import generate_image_prompt
from agent.tools import generate_scene_image

from agent.llm_graph import GraphState, llm_game_graph
from agent.models import UserState
from agent.redis_state import get_user_state

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

    user_state: UserState = await get_user_state(user_hash)
    response: Dict = {}

    ending = final_state.get("ending")
    if ending and ending.get("ending_reached"):
        ending_info = ending["ending"]
        if (
            ("description" not in ending_info or not ending_info["description"])
            and user_state.story_frame
        ):
            for e in user_state.story_frame.endings:
                if e.id == ending_info.get("id"):
                    ending_info["description"] = e.description
                    break

        ending_desc = ending_info.get("description") or ending_info.get(
            "condition", ""
        )
        change_scene = await generate_image_prompt(ending_desc, user_hash)
        # Ensure the ending always has an image. The image agent may occasionally
        # decide that no scene change is required, which would result in no
        # image generation. For endings we always want an image, so override the
        # decision if needed.
        if change_scene.change_scene == "no_change":
            change_scene.change_scene = "change_completely"
            if not change_scene.scene_description:
                change_scene.scene_description = ending_desc

        image_path = await generate_scene_image.ainvoke(
            {
                "user_hash": user_hash,
                "scene_id": f"ending_{uuid.uuid4()}",
                "change_scene": change_scene,
            }
        )

        response["ending"] = ending_info
        response["image"] = image_path
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
