"""Simple interface for querying the LLM directly."""

import logging
from typing import List, Optional

from pydantic import BaseModel, Field

from agent.llm import create_llm

logger = logging.getLogger(__name__)


class ChangeScene(BaseModel):
    """Information about a scene change."""

    change_scene: bool = Field(description="Whether the scene should change")
    scene_description: Optional[str] = None


class ChangeMusic(BaseModel):
    """Information about a music change."""

    change_music: bool = Field(description="Whether the music should change")
    music_description: Optional[str] = None


class PlayerOption(BaseModel):
    """Single option for the player."""

    option_description: str = Field(
        description=(
            "Description of the option, e.g. '[Say] Hello!' "
            "or 'Go to the forest'"
        )
    )


class LLMOutput(BaseModel):
    """Expected structure returned by the LLM."""

    change_scene: ChangeScene
    change_music: ChangeMusic
    game_message: str = Field(
        description=(
            "Message shown to the player, e.g. 'You entered the forest...'"
        )
    )
    player_options: List[PlayerOption] = Field(
        description="Up to three options for the player"
    )


_llm = create_llm().with_structured_output(LLMOutput)


async def process_user_input(text: str) -> LLMOutput:
    """Send user text to the LLM and return the parsed response."""
    logger.info("User choice: %s", text)
    response: LLMOutput = await _llm.ainvoke(text)
    logger.info("LLM response: %s", response)
    return response
