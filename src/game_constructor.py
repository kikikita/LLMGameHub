import gradio as gr
import json
import uuid
from game_setting import Character, GameSetting, get_user_story
from game_state import story, state, get_current_scene
from agent.llm_agent import process_user_input
from images.image_generator import generate_image
from game_setting import Character, GameSetting
from agent.runner import process_step
from audio.audio_generator import start_music_generation
import asyncio
from config import settings


# Predefined suggestions for demo
SETTING_SUGGESTIONS = [
    "A mystical forest shrouded in eternal twilight, where ancient trees whisper secrets and magical creatures roam freely",
    "A sprawling cyberpunk metropolis in 2099, where neon lights illuminate towering skyscrapers and technology controls every aspect of life",
    "A Victorian-era mansion on a remote cliff, filled with hidden passages, antique furniture, and an atmosphere of dark mysteries",
    "A post-apocalyptic wasteland where survivors struggle to rebuild civilization among the ruins of the old world",
    "A magical academy floating in the clouds, where young wizards learn to master their powers and uncover ancient spells",
]

CHARACTER_SUGGESTIONS = [
    {
        "name": "Elena Nightwhisper",
        "age": "25",
        "background": "A skilled detective with supernatural intuition, haunted by visions of crimes before they happen",
        "personality": "Determined, intuitive, struggles with self-doubt but fiercely protective of the innocent",
    },
    {
        "name": "Marcus Steelborn",
        "age": "32",
        "background": "A former soldier turned cybernetic engineer in a dystopian future, seeking to expose corporate corruption",
        "personality": "Brave, tech-savvy, has trust issues but deeply loyal to those who earn his respect",
    },
    {
        "name": "Aria Moonstone",
        "age": "19",
        "background": "A young witch discovering her powers while attending a prestigious magical academy",
        "personality": "Curious, ambitious, sometimes reckless but has a good heart and strong sense of justice",
    },
    {
        "name": "Dr. Victoria Blackthorne",
        "age": "45",
        "background": "A renowned archaeologist who specializes in occult artifacts and ancient mysteries",
        "personality": "Intelligent, sophisticated, perfectionist with a hidden romantic side",
    },
]

GENRE_OPTIONS = [
    "Horror - Supernatural terror and psychological thrills",
    "Detective/Mystery - Crime solving and investigation",
    "Romance - Love stories and relationship drama",
    "Fantasy - Magic and mythical creatures",
    "Sci-Fi - Futuristic technology and space exploration",
    "Adventure - Action-packed journeys and quests",
    "Psychological Thriller - Mind games and suspense",
    "Historical Fiction - Stories set in past eras",
]


def load_setting_suggestion(suggestion: str):
    """Load a predefined setting suggestion"""
    return suggestion


def load_character_suggestion(character_name: str):
    """Load a predefined character suggestion"""
    if character_name == "None":
        return "", "", "", ""

    for char in CHARACTER_SUGGESTIONS:
        if char["name"] in character_name:
            return char["name"], char["age"], char["background"], char["personality"]
    return "", "", "", ""


def save_game_config(
    setting_desc: str,
    char_name: str,
    char_age: str,
    char_background: str,
    char_personality: str,
    genre: str,
):
    """Save the game configuration to a JSON file"""
    if not all(
        [setting_desc, char_name, char_age, char_background, char_personality, genre]
    ):
        return "❌ Please fill in all fields before saving."

    config = {
        "id": str(uuid.uuid4()),
        "setting": {"description": setting_desc},
        "character": {
            "name": char_name,
            "age": char_age,
            "background": char_background,
            "personality": char_personality,
        },
        "genre": genre,
        "created_at": str(uuid.uuid4()),  # In real app, would use actual timestamp
    }

    try:
        filename = f"game_config_{config['id'][:8]}.json"
        with open(f"generated/{filename}", "w") as f:
            json.dump(config, f, indent=2)
        return f"✅ Game configuration saved as {filename}"
    except Exception as e:
        return f"❌ Error saving configuration: {str(e)}"


async def start_game_with_settings(
    user_hash: str,
    setting_desc: str,
    char_name: str,
    char_age: str,
    char_background: str,
    char_personality: str,
    genre: str,
):
    """Initialize the game with custom settings and switch to game interface"""
    if not all(
        [setting_desc, char_name, char_age, char_background, char_personality, genre]
    ):
        return (
            gr.update(visible=True),  # constructor_interface
            gr.update(visible=False),  # loading indicator
            gr.update(visible=False),  # game_interface
            gr.update(
                value="❌ Please fill in all fields before starting the game.",
                visible=True,
            ),  # error_message
            gr.update(),
            gr.update(),
            gr.update(),  # game components unchanged
            gr.update(),  # custom choice
        )

    character = Character(
        name=char_name,
        age=char_age,
        background=char_background,
        personality=char_personality,
    )

    game_setting = GameSetting(character=character, setting=setting_desc, genre=genre)

    asyncio.create_task(start_music_generation(user_hash, "neutral"))

    # Запускаем LLM-граф для инициализации истории
    result = await process_step(
        user_hash=user_hash,
        step="start",
        setting=game_setting.setting,
        character=game_setting.character.model_dump(),
        genre=game_setting.genre,
    )

    scene = result["scene"]
    scene_text = scene["description"]
    scene_image = scene.get("image", "")
    scene_choices = [ch["text"] for ch in scene.get("choices", [])]

    return (
        gr.update(visible=False),  # loading indicator
        gr.update(visible=False),  # constructor_interface
        gr.update(visible=True),  # game_interface
        gr.update(visible=False),  # error_message
        gr.update(value=scene_text),  # game_text
        gr.update(value=scene_image),  # game_image
        gr.update(choices=scene_choices, value=None),  # game_choices
        gr.update(value="", visible=True),  # custom choice
    )
