import gradio as gr
import json
import uuid
from game_setting import Character, GameSetting
from game_state import story, state, get_current_scene
from agent.llm_agent import process_user_input
from images.image_generator import generate_image
from audio.audio_generator import start_music_generation
import asyncio

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
        )

    character = Character(
        name=char_name,
        age=char_age,
        background=char_background,
        personality=char_personality,
    )

    game_setting = GameSetting(character=character, setting=setting_desc, genre=genre)

    # Initialize the game story with the custom settings
    initial_story = f"""Welcome to your story, {game_setting.character.name}!

Setting: {game_setting.setting}

You are {game_setting.character.name}, a {game_setting.character.age}-year-old character. {game_setting.character.background}

Your personality: {game_setting.character.personality}

Genre: {game_setting.genre}

You find yourself at the beginning of your adventure. The world around you feels alive with possibilities. What do you choose to do first?

NOTE FOR THE ASSISTANT: YOU HAVE TO GENERATE THE IMAGE FOR THE START SCENE.
"""

    response = await process_user_input(initial_story)
    
    music_tone = response.change_music.music_description or "neutral"
    
    asyncio.create_task(start_music_generation(user_hash, music_tone))

    img = "forest.jpg"
    
    if response.change_scene.change_scene:
        img_path, _ = await generate_image(response.change_scene.scene_description)
        if img_path:
            img = img_path

    story["start"] = {
        "text": response.game_message,
        "image": img,
        "choices": [option.option_description for option in response.player_options],
        "music_tone": response.change_music.music_description,
    }
    state["scene"] = "start"

    # Get the current scene data
    scene_text, scene_image, scene_choices = get_current_scene()

    return (
        gr.update(visible=False),  # loading indicator
        gr.update(visible=False),  # constructor_interface
        gr.update(visible=True),  # game_interface
        gr.update(visible=False),  # error_message
        gr.update(value=scene_text),  # game_text
        gr.update(value=scene_image),  # game_image
        gr.update(choices=scene_choices, value=None),  # game_choices
    )
