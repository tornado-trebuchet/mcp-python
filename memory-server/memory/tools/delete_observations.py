from typing import Annotated

from fastmcp import Context, FastMCP

from memory.model import MutationResponse, ObservationDeletion
from memory.repository import KnowledgeGraphRepository
from memory.tools._common import DESTRUCTIVE_WRITE_ANNOTATIONS, call_repository


def register_delete_observations_tool(
    mcp: FastMCP,
    repository: KnowledgeGraphRepository,
) -> None:
    @mcp.tool(
        name="delete_observations",
        title="Delete Observations",
        description="Delete specific observations from entities in the knowledge graph.",
        annotations=DESTRUCTIVE_WRITE_ANNOTATIONS,
    )
    async def delete_observations(
        deletions: Annotated[
            list[ObservationDeletion],
            "An array of observation deletions grouped by entity name",
        ],
        ctx: Context,
    ) -> MutationResponse:
        await call_repository(repository.delete_observations, deletions)
        message = "Observations deleted successfully"
        await ctx.info(message)
        return MutationResponse(success=True, message=message)