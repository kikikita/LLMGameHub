"""Async Redis-backed user state storage."""

from __future__ import annotations

import json
import msgpack
import redis.asyncio as redis

from agent.models import UserState


class UserRepository:
    """Repository for storing UserState objects in Redis."""

    def __init__(self, redis_url: str = "redis://localhost") -> None:
        self.redis = redis.from_url(redis_url)

    async def get(self, user_id: str) -> UserState:
        """Return user state for the given id, creating it if absent."""
        key = f"llmgamehub:{user_id}"
        data = await self.redis.hget(key, "data")
        if data is None:
            return UserState()
        state_dict = msgpack.unpackb(data, raw=False)
        return UserState.parse_obj(state_dict)

    async def set(self, user_id: str, state: UserState) -> None:
        """Persist updated user state."""
        key = f"llmgamehub:{user_id}"
        packed = msgpack.packb(json.loads(state.json()))
        await self.redis.hset(key, mapping={"data": packed})

    async def reset(self, user_id: str) -> None:
        """Remove stored state for a user."""
        key = f"llmgamehub:{user_id}"
        await self.redis.delete(key)


_repo = UserRepository()


async def get_user_state(user_hash: str) -> UserState:
    return await _repo.get(user_hash)


async def set_user_state(user_hash: str, state: UserState) -> None:
    await _repo.set(user_hash, state)


async def reset_user_state(user_hash: str) -> None:
    await _repo.reset(user_hash)
