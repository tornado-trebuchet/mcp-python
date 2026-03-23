from typing import Annotated

from fastmcp import Context, FastMCP

from memory.model import Relation, RelationsResponse
from memory.repository import KnowledgeGraphRepository
from memory.tools._common import IDEMPOTENT_WRITE_ANNOTATIONS, call_repository


def register_create_relations_tool(
    mcp: FastMCP,
    repository: KnowledgeGraphRepository,
) -> None:
    @mcp.tool(
        name="create_relations",
        title="Create Relations",
        description="Create multiple new relations between entities in the knowledge graph. Relations should be in active voice.",
        annotations=IDEMPOTENT_WRITE_ANNOTATIONS,
    )
    async def create_relations(
        relations: Annotated[list[Relation], "An array of relations to create"],
        ctx: Context,
    ) -> RelationsResponse:
        created_relations = await call_repository(repository.create_relations, relations)
        await ctx.info(f"Created {len(created_relations)} relations")
        return RelationsResponse(relations=created_relations)