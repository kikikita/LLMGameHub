from agent.llm import create_llm
from pydantic import BaseModel, Field
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)

class ChangeScene(BaseModel):
    change_scene: bool = Field(description="Whether the scene should be changed")
    scene_description: Optional[str] = None
    
class ChangeMusic(BaseModel):
    change_music: bool = Field(description="Whether the music should be changed")
    music_description: Optional[str] = None
    
class PlayerOption(BaseModel):
    option_description: str = Field(description="The description of the option, Examples: [Change location] Go to the forest; [Say] Hello!")
    
class LLMOutput(BaseModel):
    change_scene: ChangeScene
    change_music: ChangeMusic
    game_message: str = Field(description="The message to the player, Example: You entered the forest, and you see unknown scary creatures. What do you do?")
    player_options: List[PlayerOption] = Field(description="The list of up to 3 options for the player to choose from.")
    
llm = create_llm().with_structured_output(LLMOutput)

async def process_user_input(input: str) -> LLMOutput:
    """
    Process user input and update the state.
    """
    logger.info(f"User's choice: {input}")
    
    response: LLMOutput = await llm.ainvoke(input)
    
    logger.info(f"LLM response: {response}")
    
    return response
    