from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from sqlalchemy import create_engine, delete, or_, select
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, selectinload, sessionmaker

from memory.model import (
	Entity,
	EntityRecord,
	KnowledgeGraph,
	ObservationDeletion,
	ObservationInput,
	ObservationRecord,
	ObservationResult,
	ORMBase,
	Relation,
	RelationRecord,
)


def _dedupe_preserve_order(values: list[str]) -> list[str]:
	seen: set[str] = set()
	deduped: list[str] = []
	for value in values:
		if value in seen:
			continue
		seen.add(value)
		deduped.append(value)
	return deduped


class KnowledgeGraphRepository:
	def __init__(self, database_url: str) -> None:
		connect_args: dict[str, object] = {}
		if database_url.startswith("sqlite"):
			connect_args["check_same_thread"] = False

		self.database_url = database_url
		self.engine: Engine = create_engine(
			database_url,
			future=True,
			connect_args=connect_args,
		)
		self._session_factory = sessionmaker(
			bind=self.engine,
			expire_on_commit=False,
			class_=Session,
		)

	def initialize(self) -> None:
		if self.database_url.startswith("sqlite:///"):
			database_path = Path(self.database_url.removeprefix("sqlite:///"))
			database_path.parent.mkdir(parents=True, exist_ok=True)

		ORMBase.metadata.create_all(self.engine)

	@contextmanager
	def session(self) -> Iterator[Session]:
		with self._session_factory() as session:
			yield session

	def create_entities(self, entities: list[Entity]) -> list[Entity]:
		if not entities:
			return []

		unique_entities: list[Entity] = []
		seen_names: set[str] = set()
		for entity in entities:
			if entity.name in seen_names:
				continue
			seen_names.add(entity.name)
			unique_entities.append(entity)

		with self.session() as session:
			existing_names = set(
				session.scalars(
					select(EntityRecord.name).where(EntityRecord.name.in_(seen_names))
				).all()
			)

			new_records = [
				EntityRecord(
					name=entity.name,
					entity_type=entity.entity_type,
					observations=[
						ObservationRecord(content=content)
						for content in _dedupe_preserve_order(entity.observations)
					],
				)
				for entity in unique_entities
				if entity.name not in existing_names
			]

			session.add_all(new_records)
			session.commit()

			return [self._entity_from_record(record) for record in new_records]

	def create_relations(self, relations: list[Relation]) -> list[Relation]:
		if not relations:
			return []

		unique_relations: list[Relation] = []
		seen_keys: set[tuple[str, str, str]] = set()
		for relation in relations:
			key = (
				relation.from_entity,
				relation.to_entity,
				relation.relation_type,
			)
			if key in seen_keys:
				continue
			seen_keys.add(key)
			unique_relations.append(relation)

		with self.session() as session:
			existing_keys = {
				(record.from_entity_name, record.to_entity_name, record.relation_type)
				for record in session.scalars(
					select(RelationRecord).order_by(RelationRecord.id)
				).all()
			}

			new_records = [
				RelationRecord(
					from_entity_name=relation.from_entity,
					to_entity_name=relation.to_entity,
					relation_type=relation.relation_type,
				)
				for relation in unique_relations
				if (
					relation.from_entity,
					relation.to_entity,
					relation.relation_type,
				)
				not in existing_keys
			]

			session.add_all(new_records)
			session.commit()

			return [self._relation_from_record(record) for record in new_records]

	def add_observations(
		self,
		observations: list[ObservationInput],
	) -> list[ObservationResult]:
		if not observations:
			return []

		with self.session() as session:
			results: list[ObservationResult] = []
			for observation in observations:
				entity = session.scalar(
					select(EntityRecord)
					.options(selectinload(EntityRecord.observations))
					.where(EntityRecord.name == observation.entity_name)
				)
				if entity is None:
					raise ValueError(
						f"Entity with name {observation.entity_name} not found"
					)

				existing_observations = {
					record.content for record in entity.observations
				}
				added_observations: list[str] = []
				for content in _dedupe_preserve_order(observation.contents):
					if content in existing_observations:
						continue
					entity.observations.append(ObservationRecord(content=content))
					existing_observations.add(content)
					added_observations.append(content)

				results.append(
					ObservationResult(
						entityName=observation.entity_name,
						addedObservations=added_observations,
					)
				)

			session.commit()
			return results

	def delete_entities(self, entity_names: list[str]) -> None:
		if not entity_names:
			return

		with self.session() as session:
			session.execute(
				delete(RelationRecord).where(
					or_(
						RelationRecord.from_entity_name.in_(entity_names),
						RelationRecord.to_entity_name.in_(entity_names),
					)
				)
			)

			entities = session.scalars(
				select(EntityRecord).where(EntityRecord.name.in_(entity_names))
			).all()
			for entity in entities:
				session.delete(entity)

			session.commit()

	def delete_observations(self, deletions: list[ObservationDeletion]) -> None:
		if not deletions:
			return

		with self.session() as session:
			for deletion_request in deletions:
				entity = session.scalar(
					select(EntityRecord)
					.options(selectinload(EntityRecord.observations))
					.where(EntityRecord.name == deletion_request.entity_name)
				)
				if entity is None:
					continue

				for observation in list(entity.observations):
					if observation.content in deletion_request.observations:
						session.delete(observation)

			session.commit()

	def delete_relations(self, relations: list[Relation]) -> None:
		if not relations:
			return

		relation_keys = {
			(relation.from_entity, relation.to_entity, relation.relation_type)
			for relation in relations
		}

		with self.session() as session:
			existing_relations = session.scalars(
				select(RelationRecord).order_by(RelationRecord.id)
			).all()
			for relation in existing_relations:
				key = (
					relation.from_entity_name,
					relation.to_entity_name,
					relation.relation_type,
				)
				if key in relation_keys:
					session.delete(relation)

			session.commit()

	def read_graph(self) -> KnowledgeGraph:
		with self.session() as session:
			return self._read_graph(session)

	def search_nodes(self, query: str) -> KnowledgeGraph:
		graph = self.read_graph()
		query_lower = query.lower()
		filtered_entities = [
			entity
			for entity in graph.entities
			if query_lower in entity.name.lower()
			or query_lower in entity.entity_type.lower()
			or any(query_lower in observation.lower() for observation in entity.observations)
		]
		filtered_entity_names = {entity.name for entity in filtered_entities}
		filtered_relations = [
			relation
			for relation in graph.relations
			if relation.from_entity in filtered_entity_names
			or relation.to_entity in filtered_entity_names
		]
		return KnowledgeGraph(
			entities=filtered_entities,
			relations=filtered_relations,
		)

	def open_nodes(self, names: list[str]) -> KnowledgeGraph:
		graph = self.read_graph()
		requested_names = set(names)
		filtered_entities = [
			entity for entity in graph.entities if entity.name in requested_names
		]
		filtered_entity_names = {entity.name for entity in filtered_entities}
		filtered_relations = [
			relation
			for relation in graph.relations
			if relation.from_entity in filtered_entity_names
			or relation.to_entity in filtered_entity_names
		]
		return KnowledgeGraph(
			entities=filtered_entities,
			relations=filtered_relations,
		)

	def _read_graph(self, session: Session) -> KnowledgeGraph:
		entity_records = session.scalars(
			select(EntityRecord)
			.options(selectinload(EntityRecord.observations))
			.order_by(EntityRecord.id)
		).all()
		relation_records = session.scalars(
			select(RelationRecord).order_by(RelationRecord.id)
		).all()

		return KnowledgeGraph(
			entities=[self._entity_from_record(record) for record in entity_records],
			relations=[self._relation_from_record(record) for record in relation_records],
		)

	@staticmethod
	def _entity_from_record(record: EntityRecord) -> Entity:
		ordered_observations = sorted(
			record.observations,
			key=lambda observation: observation.id,
		)
		return Entity(
			name=record.name,
			entityType=record.entity_type,
			observations=[observation.content for observation in ordered_observations],
		)

	@staticmethod
	def _relation_from_record(record: RelationRecord) -> Relation:
		return Relation(
			**{
				"from": record.from_entity_name,
				"to": record.to_entity_name,
				"relationType": record.relation_type,
			}
		)