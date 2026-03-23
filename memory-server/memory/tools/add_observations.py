from typing import Annotated

from fastmcp import Context, FastMCP

from memory.model import ObservationInput, ObservationResultsResponse
from memory.repository import KnowledgeGraphRepository
from memory.tools._common import IDEMPOTENT_WRITE_ANNOTATIONS, call_repository


def register_add_observations_tool(
    mcp: FastMCP,
    repository: KnowledgeGraphRepository,
) -> None:
    @mcp.tool(
        name="add_observations",
        title="Add Observations",
        description="Add new observations to existing entities in the knowledge graph.",
        annotations=IDEMPOTENT_WRITE_ANNOTATIONS,
    )
    async def add_observations(
        observations: Annotated[
            list[ObservationInput],
            "An array of observation additions grouped by entity name",
        ],
        ctx: Context,
    ) -> ObservationResultsResponse:
        results = await call_repository(repository.add_observations, observations)
        total_added = sum(len(result.added_observations) for result in results)
        await ctx.info(f"Added {total_added} observations across {len(results)} entities")
        return ObservationResultsResponse(results=results)