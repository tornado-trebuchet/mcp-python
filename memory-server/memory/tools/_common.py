import asyncio
from collections.abc import Callable
from typing import ParamSpec, TypeVar

from mcp.types import ToolAnnotations

Parameters = ParamSpec("Parameters")
Result = TypeVar("Result")

READ_ONLY_ANNOTATIONS = ToolAnnotations(
    readOnlyHint=True,
    idempotentHint=True,
    openWorldHint=False,
)
IDEMPOTENT_WRITE_ANNOTATIONS = ToolAnnotations(
    readOnlyHint=False,
    destructiveHint=False,
    idempotentHint=True,
    openWorldHint=False,
)
DESTRUCTIVE_WRITE_ANNOTATIONS = ToolAnnotations(
    readOnlyHint=False,
    destructiveHint=True,
    idempotentHint=True,
    openWorldHint=False,
)


async def call_repository[**Parameters, Result](
    operation: Callable[Parameters, Result],
    *args: Parameters.args,
    **kwargs: Parameters.kwargs,
) -> Result:
    return await asyncio.to_thread(operation, *args, **kwargs)