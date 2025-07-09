from typing import Any, Dict, List


def validate_architecture_consistency(schema: Dict[str, Any]) -> List[str]:
    """Validar consistencia de arquitectura"""
    errors: List[str] = []

    entities = schema.get("entities", [])
    relationships = schema.get("relationships", [])

    entity_names = {entity.get("name") for entity in entities if entity.get("name")}

    for rel in relationships:
        from_entity = rel.get("from")
        to_entity = rel.get("to")

        if from_entity and from_entity not in entity_names:
            errors.append(f"Relación referencia entidad inexistente: {from_entity}")

        if to_entity and to_entity not in entity_names:
            errors.append(f"Relación referencia entidad inexistente: {to_entity}")

    return errors
