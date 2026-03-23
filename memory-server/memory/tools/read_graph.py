from fastmcp import Context, FastMCP

from memory.model import KnowledgeGraph
from memory.repository import KnowledgeGraphRepository
from memory.tools._common import READ_ONLY_ANNOTATIONS, call_repository


def register_read_graph_tool(
    mcp: FastMCP,
    repository: KnowledgeGraphRepository,
) -> None:
    @mcp.tool(
        name="read_graph",
        title="Read Graph",
        description="Read the entire knowledge graph.",
        annotations=READ_ONLY_ANNOTATIONS,
    )
    async def read_graph(ctx: Context) -> KnowledgeGraph:
        graph = await call_repository(repository.read_graph)
        await ctx.info(
            f"Read graph with {len(graph.entities)} entities and {len(graph.relations)} relations"
        )
        return graph