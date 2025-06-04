from agent.llm_graph import llm_game_graph, GraphState
from agent.state import get_user_state
from agent.models import UserState
from dataclasses import asdict
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
    logger.debug(f"[Runner] Building graph_state for {user_hash}: step={step}")

    # Формируем начальное состояние для графа
    graph_state = GraphState(
        user_hash=user_hash,
        step=step,
    )
    logger.debug(f"[Runner] Initial graph_state: {graph_state}")
    if step == "start":
        assert setting and character and genre, "Необходимы setting, character, genre"
        graph_state.setting = setting
        graph_state.character = character
        graph_state.genre = genre
    elif step == "choose":
        assert choice_text, "Необходимо choice_text"
        graph_state.choice_text = choice_text

    # Запускаем граф и получаем финальное состояние
    final_state = await llm_game_graph.ainvoke(asdict(graph_state))

    # Возвращаем всё нужное для UI (сцена, варианты, ассеты, ending)
    user_state: UserState = get_user_state(user_hash)
    response = {}

    logger.debug(f"[Runner] Final state after graph: {final_state}")

    ending = final_state.get("ending")
    if ending and ending.get("ending_reached"):
        response["ending"] = ending["ending"]
        response["game_over"] = True
    else:
        # Берём актуальную сцену из состояния пользователя,
        # чтобы гарантировать наличие сгенерированных ассетов
        if user_state.current_scene_id and user_state.current_scene_id in user_state.scenes:
            current_scene = user_state.scenes[user_state.current_scene_id].dict()
        else:
            current_scene = final_state.get("scene")
        response["scene"] = current_scene
        response["game_over"] = False
        # Для UI: можно вернуть пути до ассетов, варианты, текст сцены и пр.

    return response
