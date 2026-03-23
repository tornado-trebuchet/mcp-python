from functools import lru_cache
from pathlib import Path

import yaml  # type: ignore[import-untyped]
from pydantic import BaseModel, ConfigDict, Field, ValidationError


class SettingsModel(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        serialize_by_alias=True,
    )


class MemorySettings(SettingsModel):
    database_url: str = Field(
        default="sqlite:///./memory.db",
        alias="databaseUrl",
        serialization_alias="databaseUrl",
        description="SQLAlchemy database URL for durable knowledge graph storage",
    )


class ServerSettings(SettingsModel):
    name: str = Field(default="memory-server")
    instructions: str = Field(
        default=(
            "Maintain a durable knowledge graph of entities, relations, and observations. "
            "Use create_* tools for new facts, add_observations for incremental facts, "
            "and read/search/open tools to inspect the graph before mutating it."
        ),
    )
    version: str = Field(default="0.1.0")
    host: str = Field(default="127.0.0.1")
    port: int = Field(default=8000, ge=1, le=65535)
    path: str = Field(default="/")
    cors_origins: list[str] = Field(
        default_factory=list,
        alias="corsOrigins",
        serialization_alias="corsOrigins",
        description="Explicit browser origins allowed to connect to the MCP HTTP endpoint.",
    )
    cors_origin_regex: str | None = Field(
        default=r"https?://(localhost|127\.0\.0\.1)(:\d+)?$",
        alias="corsOriginRegex",
        serialization_alias="corsOriginRegex",
        description="Regex for allowed local browser origins when using direct browser-based MCP clients.",
    )


class AppSettings(SettingsModel):
    server: ServerSettings = Field(default_factory=ServerSettings)
    memory: MemorySettings = Field(default_factory=MemorySettings)

    @property
    def database_path(self) -> Path | None:
        if not self.memory.database_url.startswith("sqlite:///"):
            return None
        return Path(self.memory.database_url.removeprefix("sqlite:///"))

DEFAULT_CONFIG_PATH = Path(__file__).resolve().parent.parent / "config.yml"


def load_settings(config_path: Path | None = None) -> AppSettings:
    path = config_path or DEFAULT_CONFIG_PATH
    if not path.exists():
        return AppSettings()

    with path.open("r", encoding="utf-8") as config_file:
        raw_settings = yaml.safe_load(config_file) or {}

    try:
        return AppSettings.model_validate(raw_settings)
    except ValidationError as exc:
        raise ValueError(f"Invalid memory server configuration in {path}: {exc}") from exc


@lru_cache(maxsize=1)
def get_settings() -> AppSettings:
    return load_settings()