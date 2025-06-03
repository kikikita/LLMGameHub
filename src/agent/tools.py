from langchain_core.tools import tool
from typing import Annotated, Any, Dict, List
from agent.state import get_user_state, set_user_state
from agent.models import (
    StoryFrame,
    Scene,
    SceneChoice,
    UserChoice,
    Ending,
)
from images.image_generator import generate_image
import uuid
import logging
from agent.prompts import (
    STORY_FRAME_PROMPT,
    SCENE_PROMPT,
    ENDING_CHECK_PROMPT,
)
from agent.llm import create_llm

logger = logging.getLogger(__name__)


def _err(msg: str) -> str:
    logger.error(msg)
    return f"{{ 'error': '{msg}' }}"


def _success(msg: str) -> str:
    logger.info(msg)
    return f"{{ 'success': '{msg}' }}"


@tool
async def generate_story_frame(
    user_hash: Annotated[str, "User session ID/hash"],
    setting: Annotated[str, "Game world setting"],
    character: Annotated[Dict[str, str], "Character info"],
    genre: Annotated[str, "Genre"],
) -> Annotated[Dict, "Generated story frame"]:
    """
    Генерирует рамку истории (лор, цель, milestones, endings) через LLM и сохраняет в user state.
    """
    llm = create_llm()
    prompt = STORY_FRAME_PROMPT.format(
        setting=setting,
        character=character,
        genre=genre,
    )
    resp = await llm.ainvoke(prompt)
    # resp должен соответствовать структуре StoryFrame
    story_frame = StoryFrame(**resp)
    state = get_user_state(user_hash)
    state.story_frame = story_frame
    set_user_state(user_hash, state)
    return story_frame.dict()


@tool
async def generate_scene(
    user_hash: Annotated[str, "User session ID/hash"],
    last_choice: Annotated[str, "Last user choice or None for first scene"],
) -> Annotated[Dict, "Generated scene"]:
    """
    Генерирует новую сцену через LLM на основе story_frame и прогресса пользователя.
    """
    state = get_user_state(user_hash)
    if not state.story_frame:
        return _err("Story frame not initialized")
    llm = create_llm()
    prompt = SCENE_PROMPT.format(
        lore=state.story_frame.lore,
        goal=state.story_frame.goal,
        milestones=','.join(m.id for m in state.story_frame.milestones),
        endings=','.join(e.id for e in state.story_frame.endings),
        history='; '.join(f"{c.scene_id}:{c.choice_text}" for c in state.user_choices),
        last_choice=last_choice,
    )
    resp = await llm.ainvoke(prompt)
    # resp должен соответствовать Scene
    scene_id = str(uuid.uuid4())
    choices = [SceneChoice(**ch) for ch in resp["choices"]]
    scene = Scene(
        scene_id=scene_id,
        description=resp["description"],
        choices=choices,
        image=None,
        music=None
    )
    state.current_scene_id = scene_id
    state.scenes[scene_id] = scene
    set_user_state(user_hash, state)
    return scene.dict()


@tool
async def generate_scene_image(
    user_hash: Annotated[str, "User session ID/hash"],
    scene_id: Annotated[str, "Scene ID"],
    prompt: Annotated[str, "Prompt to generate image from"],
) -> Annotated[str, "Path to generated image"]:
    """
    Генерирует изображение для сцены, сохраняет путь в state.
    """
    try:
        image_path, img_description = await generate_image(prompt)
        state = get_user_state(user_hash)
        if scene_id in state.scenes:
            state.scenes[scene_id].image = image_path
        state.assets[scene_id] = image_path
        set_user_state(user_hash, state)
        return image_path
    except Exception as e:
        return _err(str(e))


@tool
async def update_state_with_choice(
    user_hash: Annotated[str, "User session ID/hash"],
    scene_id: Annotated[str, "Scene ID"],
    choice_text: Annotated[str, "Chosen option"],
) -> Annotated[Dict, "Updated state"]:
    """
    Обновляет state: добавляет выбор пользователя, отмечает достигнутые milestones.
    """
    import datetime
    state = get_user_state(user_hash)
    state.user_choices.append(
        UserChoice(
            scene_id=scene_id,
            choice_text=choice_text,
            timestamp=datetime.datetime.utcnow().isoformat(),
        )
    )
    # Можно добавить обновление milestones_achieved здесь, если milestone достигнут (упрощенно)
    set_user_state(user_hash, state)
    return state.dict()


@tool
async def check_ending(
    user_hash: Annotated[str, "User session ID/hash"],
) -> Annotated[Dict, "Ending check result"]:
    """
    Проверяет, достигнута ли концовка, и если да, записывает ее в state.
    """
    state = get_user_state(user_hash)
    if not state.story_frame:
        return _err("No story frame")
    llm = create_llm()
    prompt = ENDING_CHECK_PROMPT.format(
        milestones=','.join(state.milestones_achieved),
        endings=','.join(f"{e.id}:{e.condition}" for e in state.story_frame.endings),
    )
    resp = await llm.ainvoke(prompt)
    if resp.get("ending_reached"):
        ending = Ending(**resp["ending"])
        state.ending = ending
        set_user_state(user_hash, state)
        return {"ending_reached": True, "ending": ending.dict()}
    return {"ending_reached": False}
