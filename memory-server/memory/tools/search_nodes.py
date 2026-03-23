from typing import Annotated

from fastmcp import Context, FastMCP

from memory.model import KnowledgeGraph
from memory.repository import KnowledgeGraphRepository
from memory.tools._common import READ_ONLY_ANNOTATIONS, call_repository


def register_search_nodes_tool(
    mcp: FastMCP,
    repository: KnowledgeGraphRepository,
) -> None:
    @mcp.tool(
        name="search_nodes",
        title="Search Nodes",
        description="Search for nodes in the knowledge graph based on a query.",
        annotations=READ_ONLY_ANNOTATIONS,
    )
    async def search_nodes(
        query: Annotated[
            str,
            "The search query to match against entity names, types, and observation content",
        ],
        ctx: Context,
    ) -> KnowledgeGraph:
        graph = await call_repository(repository.search_nodes, query)
        await ctx.info(
            f"Search returned {len(graph.entities)} entities and {len(graph.relations)} relations"
        )
        return graph