from typing import Annotated

from fastmcp import Context, FastMCP

from memory.model import MutationResponse
from memory.repository import KnowledgeGraphRepository
from memory.tools._common import DESTRUCTIVE_WRITE_ANNOTATIONS, call_repository


def register_delete_entities_tool(
    mcp: FastMCP,
    repository: KnowledgeGraphRepository,
) -> None:
    @mcp.tool(
        name="delete_entities",
        title="Delete Entities",
        description="Delete multiple entities and their associated relations from the knowledge graph.",
        annotations=DESTRUCTIVE_WRITE_ANNOTATIONS,
    )
    async def delete_entities(
        entity_names: Annotated[list[str], "An array of entity names to delete"],
        ctx: Context,
    ) -> MutationResponse:
        await call_repository(repository.delete_entities, entity_names)
        message = "Entities deleted successfully"
        await ctx.info(message)
        return MutationResponse(success=True, message=message)