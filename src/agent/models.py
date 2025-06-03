from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Set


class Milestone(BaseModel):
    id: str
    description: str


class Ending(BaseModel):
    id: str
    type: str  # "good" / "bad"
    condition: str
    description: Optional[str] = None


class StoryFrame(BaseModel):
    lore: str
    goal: str
    milestones: List[Milestone]
    endings: List[Ending]
    setting: str
    character: Dict[str, str]
    genre: str


class StoryFrameLLM(BaseModel):
    """Output structure returned by the LLM for story frame generation."""
    lore: str
    goal: str
    milestones: List[Milestone]
    endings: List[Ending]



class SceneChoice(BaseModel):
    text: str
    next_scene_short_desc: str


class PlayerOption(BaseModel):
    option_description: str = Field(
        description=(
            "The description of the option, Examples: [Change location] Go to the forest; [Say] Hello!"
        )
    )


class Scene(BaseModel):
    scene_id: str
    description: str
    choices: List[SceneChoice]
    image: Optional[str] = None
    music: Optional[str] = None


class SceneLLM(BaseModel):
    """Structure expected from the LLM when generating a scene."""
    description: str
    choices: List[SceneChoice]


class EndingCheckResult(BaseModel):
    """Result returned from the LLM when checking for an ending."""
    ending_reached: bool = Field(default=False)
    ending: Optional[Ending] = None


class UserChoice(BaseModel):
    scene_id: str
    choice_text: str
    timestamp: Optional[str] = None


class UserState(BaseModel):
    story_frame: Optional[StoryFrame] = None
    current_scene_id: Optional[str] = None
    scenes: Dict[str, Scene] = Field(default_factory=dict)
    milestones_achieved: Set[str] = Field(default_factory=set)
    user_choices: List[UserChoice] = Field(default_factory=list)
    ending: Optional[Ending] = None
    assets: Dict[str, str] = Field(default_factory=dict)
