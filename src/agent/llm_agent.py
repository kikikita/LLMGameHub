from agent.llm import create_llm
from pydantic import BaseModel, Field
from typing import List
import logging
from agent.image_agent import ChangeScene
import asyncio
from agent.music_agent import generate_music_prompt
from agent.image_agent import generate_image_prompt
import uuid

logger = logging.getLogger(__name__)


class PlayerOption(BaseModel):
    option_description: str = Field(
        description="The description of the option, Examples: [Change location] Go to the forest; [Say] Hello!"
    )


class LLMOutput(BaseModel):
    game_message: str = Field(
        description="The message to the player, Example: You entered the forest, and you see unknown scary creatures. What do you do?"
    )
    player_options: List[PlayerOption] = Field(
        description="The list of up to 3 options for the player to choose from."
    )


class MultiAgentResponse(BaseModel):
    game_message: str = Field(
        description="The message to the player, Example: You entered the forest, and you see unknown scary creatures. What do you do?"
    )
    player_options: List[PlayerOption] = Field(
        description="The list of up to 3 options for the player to choose from."
    )
    music_prompt: str = Field(description="The prompt for the music generation model.")
    change_scene: ChangeScene = Field(description="The change to the scene.")

llm = create_llm().with_structured_output(MultiAgentResponse)


async def process_user_input(input: str) -> MultiAgentResponse:
    """
    Process user input and update the state.
    """
    request_id = str(uuid.uuid4())
    logger.info(f"LLM input received: {request_id}")

    response: LLMOutput = await llm.ainvoke(input)

    # return response
    current_state = f"""{input}
    
    Game reaction: {response.game_message}
    Player options: {response.player_options}
    """

    music_prompt_task = generate_music_prompt(current_state, request_id)
    
    change_scene_task = generate_image_prompt(current_state, request_id)
    
    music_prompt, change_scene = await asyncio.gather(music_prompt_task, change_scene_task)

    multi_agent_response = MultiAgentResponse(
        game_message=response.game_message,
        player_options=response.player_options,
        music_prompt=music_prompt,
        change_scene=change_scene,
    )
    
    logger.info(f"LLM responded: {request_id}")

    return multi_agent_response
