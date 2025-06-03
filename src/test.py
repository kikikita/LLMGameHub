import asyncio
from agent.runner import process_step
from agent.state import reset_user_state, get_user_state

USER_HASH = "test-user-123"


async def main():
    # Сбросить состояние
    reset_user_state(USER_HASH)

    # 1. Инициализация игры (жанр, setting, character)
    setting = "Тёмный город, в котором происходят странные события по ночам."
    character = {
        "name": "Иван",
        "age": "35",
        "background": "Детектив",
        "personality": "Внимательный, решительный, склонен к анализу"
    }
    genre = "Детектив"

    # Start
    print("=== START GAME ===")
    result = await process_step(
        user_hash=USER_HASH,
        step="start",
        setting=setting,
        character=character,
        genre=genre
    )
    print("Game started. Scene:", result["scene"]["description"])
    for idx, ch in enumerate(result["scene"]["choices"]):
        print(f"Choice {idx+1}: {ch['text']}")
    # Эмулируем выбор игрока (например, первый)
    choice_text = result["scene"]["choices"][0]["text"]

    # 2. Первый шаг игрока
    print("\n=== PLAYER CHOICE 1 ===")
    result = await process_step(
        user_hash=USER_HASH,
        step="choose",
        choice_text=choice_text
    )
    if result["game_over"]:
        print("Game ended:", result["ending"]["description"])
        return

    print("Scene:", result["scene"]["description"])
    for idx, ch in enumerate(result["scene"]["choices"]):
        print(f"Choice {idx+1}: {ch['text']}")

    # 3. Второй ход (опционально)
    choice_text = result["scene"]["choices"][0]["text"]
    print("\n=== PLAYER CHOICE 2 ===")
    result = await process_step(
        user_hash=USER_HASH,
        step="choose",
        choice_text=choice_text
    )
    if result["game_over"]:
        print("Game ended:", result["ending"]["description"])
        return

    print("Scene:", result["scene"]["description"])
    for idx, ch in enumerate(result["scene"]["choices"]):
        print(f"Choice {idx+1}: {ch['text']}")


if __name__ == "__main__":
    asyncio.run(main())
