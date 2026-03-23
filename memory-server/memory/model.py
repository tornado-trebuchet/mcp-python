from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class ORMBase(DeclarativeBase):
	pass


class EntityRecord(ORMBase):
	__tablename__ = "entities"

	id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
	name: Mapped[str] = mapped_column(String(255), unique=True, index=True)
	entity_type: Mapped[str] = mapped_column(String(255), index=True)

	observations: Mapped[list[ObservationRecord]] = relationship(
		back_populates="entity",
		cascade="all, delete-orphan",
		passive_deletes=True,
	)


class ObservationRecord(ORMBase):
	__tablename__ = "observations"
	__table_args__ = (
		UniqueConstraint("entity_id", "content", name="uq_entity_observation"),
	)

	id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
	entity_id: Mapped[int] = mapped_column(
		ForeignKey("entities.id", ondelete="CASCADE"),
		index=True,
	)
	content: Mapped[str] = mapped_column(String(2048))

	entity: Mapped[EntityRecord] = relationship(back_populates="observations")


class RelationRecord(ORMBase):
	__tablename__ = "relations"
	__table_args__ = (
		UniqueConstraint(
			"from_entity_name",
			"to_entity_name",
			"relation_type",
			name="uq_relation_edge",
		),
	)

	id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
	from_entity_name: Mapped[str] = mapped_column(String(255), index=True)
	to_entity_name: Mapped[str] = mapped_column(String(255), index=True)
	relation_type: Mapped[str] = mapped_column(String(255), index=True)


class GraphModel(BaseModel):
	model_config = ConfigDict(
		populate_by_name=True,
		serialize_by_alias=True,
	)


class Entity(GraphModel):
	name: str = Field(description="The name of the entity")
	entity_type: str = Field(
		alias="entityType",
		serialization_alias="entityType",
		description="The type of the entity",
	)
	observations: list[str] = Field(
		default_factory=list,
		description="An array of observation contents associated with the entity",
	)


class Relation(GraphModel):
	from_entity: str = Field(
		alias="from",
		serialization_alias="from",
		description="The name of the entity where the relation starts",
	)
	to_entity: str = Field(
		alias="to",
		serialization_alias="to",
		description="The name of the entity where the relation ends",
	)
	relation_type: str = Field(
		alias="relationType",
		serialization_alias="relationType",
		description="The type of the relation",
	)


class ObservationInput(GraphModel):
	entity_name: str = Field(
		alias="entityName",
		serialization_alias="entityName",
		description="The name of the entity to add the observations to",
	)
	contents: list[str] = Field(
		description="An array of observation contents to add",
	)


class ObservationDeletion(GraphModel):
	entity_name: str = Field(
		alias="entityName",
		serialization_alias="entityName",
		description="The name of the entity containing the observations",
	)
	observations: list[str] = Field(
		description="An array of observations to delete",
	)


class ObservationResult(GraphModel):
	entity_name: str = Field(
		alias="entityName",
		serialization_alias="entityName",
	)
	added_observations: list[str] = Field(
		alias="addedObservations",
		serialization_alias="addedObservations",
	)


class KnowledgeGraph(GraphModel):
	entities: list[Entity] = Field(default_factory=list)
	relations: list[Relation] = Field(default_factory=list)


class EntitiesResponse(GraphModel):
	entities: list[Entity]


class RelationsResponse(GraphModel):
	relations: list[Relation]


class ObservationResultsResponse(GraphModel):
	results: list[ObservationResult]


class MutationResponse(GraphModel):
	success: bool
	message: str