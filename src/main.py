import gradio as gr
from css import custom_css, loading_css_styles
from audio.audio_generator import (
    update_audio,
    cleanup_music_session,
)
import logging
from agent.llm_agent import process_user_input
from images.image_generator import modify_image
from agent.runner import process_step
import uuid
from game_constructor import (
    SETTING_SUGGESTIONS,
    CHARACTER_SUGGESTIONS,
    GENRE_OPTIONS,
    load_setting_suggestion,
    load_character_suggestion,
    start_game_with_settings,
)
import asyncio
from game_setting import get_user_story
from config import settings

logger = logging.getLogger(__name__)


async def return_to_constructor(user_hash: str):
    """Return to the constructor and reset user state and audio."""
    from agent.state import reset_user_state

    reset_user_state(user_hash)
    await cleanup_music_session(user_hash)
    # Generate a new hash to avoid stale state
    new_hash = str(uuid.uuid4())
    return (
        gr.update(visible=False),  # loading_indicator
        gr.update(visible=True),  # constructor_interface
        gr.update(visible=False),  # game_interface
        gr.update(visible=False),  # error_message
        gr.update(value=new_hash),  # local_storage
    )


async def update_scene(user_hash: str, choice):
    logger.info(f"Updating scene with choice: {choice}")
    if not isinstance(choice, str):
        return gr.update(), gr.update(), gr.update(), gr.update()

    result = await process_step(
        user_hash=user_hash,
        step="choose",
        choice_text=choice,
    )

    if result.get("game_over"):
        ending = result["ending"]
        ending_text = ending.get("description") or ending.get("condition", "")
        return (
            gr.update(value=ending_text),
            gr.update(value=None),
            gr.Radio(choices=[], label="", value=None, visible=False),
            gr.update(value="", visible=False),
        )

    scene = result["scene"]
    return (
        scene["description"],
        scene.get("image", ""),
        gr.Radio(
            choices=[ch["text"] for ch in scene.get("choices", [])],
            label="What do you choose? (select an option or write your own)",
            value=None,
            elem_classes=["choice-buttons"],
        ),
        gr.update(value=""),
    )


def update_preview(setting, name, age, background, personality, genre):
    """Update the configuration preview"""
    if not any([setting, name, age, background, personality]):
        return "Fill in the fields to see a preview..."

    preview = f"""🌍 SETTING: {setting[:100]}{"..." if len(setting) > 100 else ""}

👤 CHARACTER: {name} (Age: {age})
📖 Background: {background}
💭 Personality: {personality}

🎭 GENRE: {genre}"""
    return preview


async def start_game_with_music(
    user_hash: str,
    setting_desc: str,
    char_name: str,
    char_age: str,
    char_background: str,
    char_personality: str,
    genre: str,
):
    """Start the game with custom settings and initialize music"""
    yield (
        gr.update(visible=True),  # loading indicator
        gr.update(),  # constructor_interface
        gr.update(),  # game_interface
        gr.update(),  # error_message
        gr.update(),
        gr.update(),
        gr.update(),  # game components unchanged
        gr.update(),  # custom choice unchanged
    )

    # First, get the game interface updates
    result = await start_game_with_settings(
        user_hash,
        setting_desc,
        char_name,
        char_age,
        char_background,
        char_personality,
        genre,
    )
    yield result


with gr.Blocks(
    theme="soft",
    title="Game Constructor & Visual Novel",
    css=custom_css + loading_css_styles,
) as demo:
    # Fullscreen Loading Indicator (hidden by default)
    with gr.Column(visible=False, elem_id="loading-indicator") as loading_indicator:
        gr.HTML("<div class='loading-text'>🚀 Starting your adventure...</div>")

    local_storage = gr.BrowserState(str(uuid.uuid4()), "user_hash")

    # Constructor Interface (visible by default)
    with gr.Column(
        visible=True, elem_id="constructor-interface"
    ) as constructor_interface:
        gr.Markdown("# 🎮 Interactive Game Constructor")
        gr.Markdown(
            "Create your own interactive story game by defining the setting, character, and genre!"
        )

        # Error message area
        error_message = gr.Textbox(
            label="⚠️ Error",
            visible=False,
            interactive=False,
            elem_classes=["error-message"],
        )

        with gr.Row():
            with gr.Column(scale=2):
                # Setting Description Section
                with gr.Group():
                    gr.Markdown("## 🌍 Setting Description")
                    setting_suggestions = gr.Dropdown(
                        choices=["Select a suggestion..."] + SETTING_SUGGESTIONS,
                        label="Quick Suggestions",
                        value="Select a suggestion...",
                        interactive=True,
                    )
                    setting_description = gr.Textbox(
                        label="Describe your game setting",
                        placeholder="Enter a detailed description of where your story takes place...",
                        lines=4,
                        max_lines=6,
                    )

                # Character Description Section
                with gr.Group():
                    gr.Markdown("## 👤 Character Description")
                    character_suggestions = gr.Dropdown(
                        choices=["None"]
                        + [
                            f"{char['name']} - {char['background'][:50]}..."
                            for char in CHARACTER_SUGGESTIONS
                        ],
                        label="Character Templates",
                        value="None",
                        interactive=True,
                    )

                    with gr.Row():
                        char_name = gr.Textbox(
                            label="Character Name",
                            placeholder="Enter character name...",
                        )
                        char_age = gr.Textbox(label="Age", placeholder="25")

                    char_background = gr.Textbox(
                        label="Background/Profession",
                        placeholder="Describe your character's background, profession, or role...",
                        lines=2,
                    )
                    char_personality = gr.Textbox(
                        label="Personality & Traits",
                        placeholder="Describe personality, quirks, motivations, fears...",
                        lines=2,
                    )

                # Genre Selection Section
                with gr.Group():
                    gr.Markdown("## 🎭 Genre & Style")
                    genre_selection = gr.Dropdown(
                        choices=GENRE_OPTIONS,
                        label="Choose your story genre",
                        value=GENRE_OPTIONS[0],
                        interactive=True,
                    )

            with gr.Column(scale=1):
                # Preview Section
                with gr.Group():
                    gr.Markdown("## 📋 Configuration Preview")
                    preview_box = gr.Textbox(
                        label="Game Summary",
                        lines=8,
                        interactive=False,
                        placeholder="Fill in the fields to see a preview...",
                    )

                with gr.Group():
                    gr.Markdown("## 🎮 Ready to Play?")
                    start_btn = gr.Button("▶️ Start Game", variant="primary", size="lg")

    with gr.Column(visible=False, elem_id="game-interface") as game_interface:
        gr.Markdown("# 🎮 Your Interactive Story")

        with gr.Row():
            gr.Markdown("### Playing your custom game!")
        back_btn = gr.Button(
            "⬅️ Back to Constructor",
            variant="secondary",
            elem_id="back-btn",
        )

        # Audio component for background music
        audio_out = gr.Audio(
            autoplay=True, streaming=True, interactive=False, visible=False
        )

        # Background image (fullscreen)
        with gr.Column(elem_classes=["image-container"]):
            game_image = gr.Image(type="filepath", interactive=False, show_label=False)

        # Overlay content (text and buttons)
        with gr.Column(elem_classes=["overlay-content"]):
            game_text = gr.Textbox(
                label="",
                interactive=False,
                show_label=False,
                elem_classes=["narrative-text"],
                lines=3,
            )
            with gr.Column(elem_classes=["choice-area"]):
                game_choices = gr.Radio(
                    choices=[],
                    label="What do you choose? (select an option or write your own)",
                    value=None,
                    elem_classes=["choice-buttons"],
                )
                custom_choice = gr.Textbox(
                    label="",
                    show_label=False,
                    placeholder="Type your option and press Enter",
                    lines=1,
                    elem_classes=["choice-input"],
                )

    # Event handlers for constructor interface
    setting_suggestions.change(
        fn=load_setting_suggestion,
        inputs=[setting_suggestions],
        outputs=[setting_description],
    )

    character_suggestions.change(
        fn=load_character_suggestion,
        inputs=[character_suggestions],
        outputs=[char_name, char_age, char_background, char_personality],
    )

    # Update preview when any field changes
    for component in [
        setting_description,
        char_name,
        char_age,
        char_background,
        char_personality,
        genre_selection,
    ]:
        component.change(
            fn=update_preview,
            inputs=[
                setting_description,
                char_name,
                char_age,
                char_background,
                char_personality,
                genre_selection,
            ],
            outputs=[preview_box],
        )

    # Interface switching handlers
    start_btn.click(
        fn=start_game_with_music,
        inputs=[
            local_storage,
            setting_description,
            char_name,
            char_age,
            char_background,
            char_personality,
            genre_selection,
        ],
        outputs=[
            loading_indicator,
            constructor_interface,
            game_interface,
            error_message,
            game_text,
            game_image,
            game_choices,
            custom_choice,
        ],
    )

    back_btn.click(
        fn=return_to_constructor,
        inputs=[local_storage],
        outputs=[
            loading_indicator,
            constructor_interface,
            game_interface,
            error_message,
            local_storage,
        ],
    )

    game_choices.change(
        fn=update_scene,
        inputs=[local_storage, game_choices],
        outputs=[game_text, game_image, game_choices, custom_choice],
    )

    custom_choice.submit(
        fn=update_scene,
        inputs=[local_storage, custom_choice],
        outputs=[game_text, game_image, game_choices, custom_choice],
    )

    demo.unload(cleanup_music_session)
    demo.load(
        fn=update_audio,
        inputs=[local_storage],
        outputs=[audio_out],
    )

demo.launch(ssr_mode=False)
