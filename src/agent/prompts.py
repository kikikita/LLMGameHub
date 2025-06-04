STORY_FRAME_PROMPT = """
You are a narrative game designer. Use the player data below to
create a story frame for an interactive adventure.
Setting: {setting}
Character: {character}
Genre: {genre}
Return ONLY a JSON object with:
- lore: brief world description
- goal: main player objective
- milestones: 2-4 key events (id, description)
- endings: good/bad endings (id, type, condition, description)
Translate the lore, goal, milestones and endings into
a langueage of setting language.
"""

SCENE_PROMPT = """
Using the provided lore and history, generate the next scene.
Lore: {lore}
Goal: {goal}
Milestones: {milestones}
Endings: {endings}
History: {history}
Last choice: {last_choice}
Respond ONLY with JSON containing:
- description: short summary of the scene
- choices: exactly two dicts {{"text": ..., "next_scene_short_desc": ...}}
Translate the scene description and choices into a language of lore language.
"""

ENDING_CHECK_PROMPT = """
History: {history}
Endings: {endings}
Check if any ending conditions are met.
If none are met return ending_reached: false.
If an ending is reached return ending_reached: true and provide the
ending object (id, type, description).
Respond ONLY with JSON.
"""
