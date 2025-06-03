from agent.llm_graph import llm_game_graph
from agent.state import get_user_state
from agent.models import UserState
import logging

logger = logging.getLogger(__name__)


async def process_step(
    user_hash: str,
    step: str,
    setting: str = None,
    character: dict = None,
    genre: str = None,
    choice_text: str = None,
) -> dict:
    """
    Основная точка входа для обработки шага пользователя.
    - step: "start" — начало игры
    - step: "choose" — пользователь делает выбор
    """
    logger.info(f"[Runner] Step: {step}, user: {user_hash}")

    # Формируем начальное состояние для графа
    graph_state = {
        "user_hash": user_hash,
        "step": step,
    }
    if step == "start":
        assert setting and character and genre, "Необходимы setting, character, genre"
        graph_state.update({
            "setting": setting,
            "character": character,
            "genre": genre,
        })
    elif step == "choose":
        assert choice_text, "Необходимо choice_text"
        graph_state["choice_text"] = choice_text

    # Запускаем граф (асинхронно, один проход)
    async for final_state in llm_game_graph.astream(graph_state):
            pass

    # Возвращаем всё нужное для UI (сцена, варианты, ассеты, ending)
    user_state: UserState = get_user_state(user_hash)
    response = {}

    if final_state.get("ending", {}).get("ending_reached"):
        response["ending"] = final_state["ending"]["ending"]
        response["game_over"] = True
    else:
        current_scene = final_state.get("scene")
        response["scene"] = current_scene
        response["game_over"] = False
        # Для UI: можно вернуть пути до ассетов, варианты, текст сцены и пр.

    return response
