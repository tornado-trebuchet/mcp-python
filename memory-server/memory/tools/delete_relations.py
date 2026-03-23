from typing import Annotated

from fastmcp import Context, FastMCP

from memory.model import MutationResponse, Relation
from memory.repository import KnowledgeGraphRepository
from memory.tools._common import DESTRUCTIVE_WRITE_ANNOTATIONS, call_repository


def register_delete_relations_tool(
    mcp: FastMCP,
    repository: KnowledgeGraphRepository,
) -> None:
    @mcp.tool(
        name="delete_relations",
        title="Delete Relations",
        description="Delete multiple relations from the knowledge graph.",
        annotations=DESTRUCTIVE_WRITE_ANNOTATIONS,
    )
    async def delete_relations(
        relations: Annotated[list[Relation], "An array of relations to delete"],
        ctx: Context,
    ) -> MutationResponse:
        await call_repository(repository.delete_relations, relations)
        message = "Relations deleted successfully"
        await ctx.info(message)
        return MutationResponse(success=True, message=message)