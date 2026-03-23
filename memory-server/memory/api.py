from fastmcp import FastMCP
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.routing import Mount

from memory.repository import KnowledgeGraphRepository
from memory.settings import get_settings
from memory.tools import register_tools


def create_repository() -> KnowledgeGraphRepository:
	settings = get_settings()
	repository = KnowledgeGraphRepository(settings.memory.database_url)
	repository.initialize()
	return repository


def create_server(
	repository: KnowledgeGraphRepository | None = None,
) -> FastMCP:
	settings = get_settings()
	graph_repository = repository or create_repository()

	mcp = FastMCP(
		name=settings.server.name,
		instructions=settings.server.instructions,
		version=settings.server.version,
		on_duplicate="error",
	)
	register_tools(mcp, graph_repository)
	return mcp


def create_app(
	repository: KnowledgeGraphRepository | None = None,
) -> Starlette:
	settings = get_settings()
	mcp = create_server(repository)
	mcp_app = mcp.http_app(path="/")
	middleware = [
		Middleware(
			CORSMiddleware,
			allow_origins=settings.server.cors_origins,
			allow_origin_regex=settings.server.cors_origin_regex,
			allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
			allow_headers=[
				"Accept",
				"Authorization",
				"Content-Type",
				"mcp-protocol-version",
				"mcp-session-id",
			],
			expose_headers=["mcp-session-id"],
		)
	]

	return Starlette(
		routes=[Mount(settings.server.path, app=mcp_app)],
		middleware=middleware,
		lifespan=mcp_app.lifespan,
	)


app = create_app()