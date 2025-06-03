STORY_FRAME_PROMPT = """
Ты — автор интерактивных сюжетных игр. Используй данные игрока.
Setting: {setting}
Character: {character}
Genre: {genre}
Сформируй структуру JSON с ключами:
- lore: краткое описание мира
- goal: основная цель игрока
- milestones: 2-4 важных события (id, description)
- endings: good/bad endings (id, type, condition, description)
"""

SCENE_PROMPT = """
Используй лор: {lore}
Цель: {goal}
Milestones: {milestones}
Endings: {endings}
История: {history}
Последний выбор: {last_choice}
Сгенерируй новую сцену в формате:
- description: короткое описание ситуации
- choices: список из 2-3 dict {"text": ..., "next_scene_short_desc": ...}
"""

ENDING_CHECK_PROMPT = """
Milestones achieved: {milestones}
Endings: {endings}
Проверь, выполнены ли условия концовки. Если да, верни ending_reached: true и ending (id, type, description).
Если нет — ending_reached: false.
"""
