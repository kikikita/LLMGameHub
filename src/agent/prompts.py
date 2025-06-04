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
Отвечай ТОЛЬКО JSON без пояснений.
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
- choices: список ИМЕННО из двух dict {{"text": ..., "next_scene_short_desc": ...}}
Отвечай ТОЛЬКО JSON без пояснений.
"""

ENDING_CHECK_PROMPT = """
История действий игрока: {history}
Endings: {endings}
Проанализируй историю и определи, выполнены ли условия для какой-либо концовки. 
Если ни одно условие не выполнено, верни ending_reached: false.
Если условие выполнено, укажи ending_reached: true и верни объект ending (id, type, description).
Отвечай ТОЛЬКО JSON без пояснений.
"""
