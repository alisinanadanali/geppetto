"""arq WorkerSettings iskeleti. Görevler bölüm 6.9'da eklenir."""

from collections.abc import Callable, Coroutine
from typing import Any, ClassVar

from arq.connections import RedisSettings


async def ping(ctx: dict[str, object]) -> str:
    return "pong"


class WorkerSettings:
    functions: ClassVar[list[Callable[..., Coroutine[Any, Any, Any]]]] = [ping]
    redis_settings = RedisSettings()
