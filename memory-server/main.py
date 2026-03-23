import uvicorn

from memory.api import create_app
from memory.settings import get_settings

settings = get_settings()

app = create_app()


if __name__ == "__main__":
	uvicorn.run(
		app,
		host=settings.server.host,
		port=settings.server.port,
		ws="none",
	)
