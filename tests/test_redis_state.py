import os
import sys

import pytest
import fakeredis

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from agent import redis_state
from agent.models import UserState


@pytest.mark.asyncio
async def test_user_repository_get_set_reset(monkeypatch):
    fake = fakeredis.FakeAsyncRedis()
    repo = redis_state.UserRepository()
    repo.redis = fake
    monkeypatch.setattr(redis_state, "_repo", repo)

    user_id = "user123"
    state = UserState(current_scene_id="scene1")

    await redis_state.set_user_state(user_id, state)
    fetched = await redis_state.get_user_state(user_id)
    assert fetched.current_scene_id == "scene1"

    await redis_state.reset_user_state(user_id)
    reset_state = await redis_state.get_user_state(user_id)
    assert reset_state.current_scene_id is None
