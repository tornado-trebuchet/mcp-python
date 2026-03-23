from typing import Annotated

from fastmcp import Context, FastMCP

from memory.model import KnowledgeGraph
from memory.repository import KnowledgeGraphRepository
from memory.tools._common import READ_ONLY_ANNOTATIONS, call_repository


def register_open_nodes_tool(
    mcp: FastMCP,
    repository: KnowledgeGraphRepository,
) -> None:
    @mcp.tool(
        name="open_nodes",
        title="Open Nodes",
        description="Open specific nodes in the knowledge graph by their names.",
        annotations=READ_ONLY_ANNOTATIONS,
    )
    async def open_nodes(
        names: Annotated[list[str], "An array of entity names to retrieve"],
        ctx: Context,
    ) -> KnowledgeGraph:
        graph = await call_repository(repository.open_nodes, names)
        await ctx.info(
            f"Opened {len(graph.entities)} entities and {len(graph.relations)} relations"
        )
        return graph