from fastmcp import FastMCP

from memory.repository import KnowledgeGraphRepository
from memory.tools.add_observations import register_add_observations_tool
from memory.tools.create_entities import register_create_entities_tool
from memory.tools.create_relations import register_create_relations_tool
from memory.tools.delete_entities import register_delete_entities_tool
from memory.tools.delete_observations import register_delete_observations_tool
from memory.tools.delete_relations import register_delete_relations_tool
from memory.tools.open_nodes import register_open_nodes_tool
from memory.tools.read_graph import register_read_graph_tool
from memory.tools.search_nodes import register_search_nodes_tool


def register_tools(mcp: FastMCP, repository: KnowledgeGraphRepository) -> None:
	register_create_entities_tool(mcp, repository)
	register_create_relations_tool(mcp, repository)
	register_add_observations_tool(mcp, repository)
	register_delete_entities_tool(mcp, repository)
	register_delete_observations_tool(mcp, repository)
	register_delete_relations_tool(mcp, repository)
	register_read_graph_tool(mcp, repository)
	register_search_nodes_tool(mcp, repository)
	register_open_nodes_tool(mcp, repository)
