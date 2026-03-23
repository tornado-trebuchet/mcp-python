from typing import Annotated

from fastmcp import Context, FastMCP

from memory.model import EntitiesResponse, Entity
from memory.repository import KnowledgeGraphRepository
from memory.tools._common import IDEMPOTENT_WRITE_ANNOTATIONS, call_repository


def register_create_entities_tool(
    mcp: FastMCP,
    repository: KnowledgeGraphRepository,
) -> None:
    @mcp.tool(
        name="create_entities",
        title="Create Entities",
        description="Create multiple new entities in the knowledge graph.",
        annotations=IDEMPOTENT_WRITE_ANNOTATIONS,
    )
    async def create_entities(
        entities: Annotated[list[Entity], "An array of entities to create"],
        ctx: Context,
    ) -> EntitiesResponse:
        created_entities = await call_repository(repository.create_entities, entities)
        await ctx.info(f"Created {len(created_entities)} entities")
        return EntitiesResponse(entities=created_entities)