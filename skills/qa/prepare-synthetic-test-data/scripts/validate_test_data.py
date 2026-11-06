#!/usr/bin/env python3
"""Validate synthetic QA data without running tests or contacting a service."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence
from urllib.parse import urlparse


class ValidationError(ValueError):
    """Raised when a path, JSON document, or data contract is invalid."""


def reject_duplicate_keys(pairs: Sequence[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValidationError(f"clave JSON duplicada: {key}")
        result[key] = value
    return result


def load_json_object(path: Path, label: str) -> Mapping[str, Any]:
    if path.is_symlink():
        raise ValidationError(f"{label} no puede ser un symlink: {path}")
    if not path.is_file():
        raise ValidationError(f"{label} debe ser un archivo existente: {path}")
    try:
        value = json.loads(
            path.read_text(encoding="utf-8"),
            object_pairs_hook=reject_duplicate_keys,
        )
    except OSError as error:
        raise ValidationError(f"no se pudo leer {label}: {error}") from error
    except json.JSONDecodeError as error:
        raise ValidationError(f"JSON inválido en {label}: {error}") from error
    if not isinstance(value, dict):
        raise ValidationError(f"la raíz de {label} debe ser un objeto JSON")
    return value


def require_exact_keys(
    value: Mapping[str, Any], required: set[str], allowed: set[str], label: str
) -> None:
    missing = sorted(required - set(value))
    unexpected = sorted(set(value) - allowed)
    if missing:
        raise ValidationError(f"{label} omite campos obligatorios: {', '.join(missing)}")
    if unexpected:
        raise ValidationError(f"{label} contiene campos no permitidos: {', '.join(unexpected)}")


def require_text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"{label} debe ser un texto no vacío")
    return value


def validate_case_list(value: Any, case_pattern: str, label: str) -> list[str]:
    if not isinstance(value, list) or not value:
        raise ValidationError(f"{label} debe ser una lista no vacía")
    if not all(isinstance(item, str) for item in value):
        raise ValidationError(f"{label} solo puede contener textos")
    if len(value) != len(set(value)):
        raise ValidationError(f"{label} contiene duplicados")
    if any(re.fullmatch(case_pattern, item) is None for item in value):
        raise ValidationError(f"{label} contiene un identificador inválido")
    return value


def validate_synthetic_string(value: str, label: str) -> None:
    if "@" in value:
        local, separator, domain = value.rpartition("@")
        if not separator or not local or not domain.casefold().endswith(".test"):
            raise ValidationError(f"{label} contiene un correo fuera de un dominio .test")
    if value.startswith(("http://", "https://")):
        host = urlparse(value).hostname
        if host is None or not host.casefold().endswith(".test"):
            raise ValidationError(f"{label} contiene una URL que no usa un dominio .test")


def validate_contract(data: Mapping[str, Any], schema: Mapping[str, Any]) -> int:
    if schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
        raise ValidationError("el schema debe declarar JSON Schema draft 2020-12")

    properties = schema.get("properties")
    definitions = schema.get("$defs")
    required = schema.get("required")
    if not isinstance(properties, dict) or not isinstance(definitions, dict):
        raise ValidationError("el schema no contiene properties y $defs válidos")
    if not isinstance(required, list) or not all(isinstance(item, str) for item in required):
        raise ValidationError("el schema no contiene required válido")
    require_exact_keys(data, set(required), set(properties), "documento")

    expected_version = properties.get("schemaVersion", {}).get("const")
    expected_classification = properties.get("classification", {}).get("const")
    if data.get("schemaVersion") != expected_version:
        raise ValidationError(f"schemaVersion debe ser {expected_version!r}")
    if data.get("classification") != expected_classification:
        raise ValidationError("classification debe ser synthetic")

    story_pattern = properties.get("story", {}).get("pattern")
    case_pattern = definitions.get("caseId", {}).get("pattern")
    if not isinstance(story_pattern, str) or not isinstance(case_pattern, str):
        raise ValidationError("el schema omite patrones de story o caseId")
    story = require_text(data.get("story"), "story")
    if re.fullmatch(story_pattern, story) is None:
        raise ValidationError("story no cumple el patrón publicado")

    document_cases = validate_case_list(data.get("cases"), case_pattern, "cases")
    known_cases = set(document_cases)

    record_schema = definitions.get("record")
    if not isinstance(record_schema, dict):
        raise ValidationError("el schema omite la definición record")
    record_properties = record_schema.get("properties")
    record_required = record_schema.get("required")
    if not isinstance(record_properties, dict) or not isinstance(record_required, list):
        raise ValidationError("la definición record del schema es inválida")
    record_id_pattern = record_properties.get("id", {}).get("pattern")
    categories = record_properties.get("category", {}).get("enum")
    backend_states = record_properties.get("backendState", {}).get("enum")
    if not isinstance(record_id_pattern, str):
        raise ValidationError("el schema omite el patrón de record.id")
    if not isinstance(categories, list) or not isinstance(backend_states, list):
        raise ValidationError("el schema omite categorías o estados permitidos")

    records = data.get("records")
    if not isinstance(records, list):
        raise ValidationError("records debe ser una lista")
    record_ids: set[str] = set()
    primitive_types = (str, int, float, bool, type(None))
    for index, raw_record in enumerate(records):
        label = f"records[{index}]"
        if not isinstance(raw_record, dict):
            raise ValidationError(f"{label} debe ser un objeto")
        require_exact_keys(
            raw_record,
            set(record_required),
            set(record_properties),
            label,
        )
        record_id = require_text(raw_record.get("id"), f"{label}.id")
        if re.fullmatch(record_id_pattern, record_id) is None:
            raise ValidationError(f"{label}.id no cumple el patrón publicado")
        if record_id in record_ids:
            raise ValidationError(f"id de record duplicado: {record_id}")
        record_ids.add(record_id)

        record_cases = validate_case_list(
            raw_record.get("cases"), case_pattern, f"{label}.cases"
        )
        unknown_cases = sorted(set(record_cases) - known_cases)
        if unknown_cases:
            raise ValidationError(
                f"{label}.cases referencia casos no declarados: {', '.join(unknown_cases)}"
            )
        if raw_record.get("category") not in categories:
            raise ValidationError(f"{label}.category no está permitida")
        if raw_record.get("backendState") not in backend_states:
            raise ValidationError(f"{label}.backendState no está permitido")

        values = raw_record.get("values")
        if not isinstance(values, dict) or not values:
            raise ValidationError(f"{label}.values debe ser un objeto no vacío")
        for key, value in values.items():
            require_text(key, f"{label}.values key")
            if not isinstance(value, primitive_types):
                raise ValidationError(f"{label}.values.{key} debe ser un valor primitivo")
            if isinstance(value, str):
                if not value:
                    raise ValidationError(f"{label}.values.{key} no puede estar vacío")
                validate_synthetic_string(value, f"{label}.values.{key}")

        constraints = raw_record.get("constraints")
        if not isinstance(constraints, list) or not constraints:
            raise ValidationError(f"{label}.constraints debe ser una lista no vacía")
        for constraint_index, constraint in enumerate(constraints):
            constraint_label = f"{label}.constraints[{constraint_index}]"
            if not isinstance(constraint, dict):
                raise ValidationError(f"{constraint_label} debe ser un objeto")
            require_exact_keys(
                constraint,
                {"field", "rule", "source"},
                {"field", "rule", "source"},
                constraint_label,
            )
            for field in ("field", "rule", "source"):
                require_text(constraint.get(field), f"{constraint_label}.{field}")

    sources = data.get("sources")
    if not isinstance(sources, list) or not sources:
        raise ValidationError("sources debe ser una lista no vacía")
    for index, source in enumerate(sources):
        label = f"sources[{index}]"
        if not isinstance(source, dict):
            raise ValidationError(f"{label} debe ser un objeto")
        require_exact_keys(
            source,
            {"id", "path", "revision"},
            {"id", "path", "revision"},
            label,
        )
        for field in ("id", "path", "revision"):
            require_text(source.get(field), f"{label}.{field}")

    seed_requirements = data.get("seedRequirements")
    if not isinstance(seed_requirements, list):
        raise ValidationError("seedRequirements debe ser una lista")
    seed_statuses = definitions.get("seedRequirement", {}).get("properties", {}).get(
        "status", {}
    ).get("enum")
    if not isinstance(seed_statuses, list):
        raise ValidationError("el schema omite estados de seed permitidos")
    for index, requirement in enumerate(seed_requirements):
        label = f"seedRequirements[{index}]"
        if not isinstance(requirement, dict):
            raise ValidationError(f"{label} debe ser un objeto")
        require_exact_keys(
            requirement,
            {"case", "status", "owner", "reference"},
            {"case", "status", "owner", "reference"},
            label,
        )
        case = require_text(requirement.get("case"), f"{label}.case")
        if case not in known_cases:
            raise ValidationError(f"{label}.case no está declarado en cases")
        if requirement.get("status") not in seed_statuses:
            raise ValidationError(f"{label}.status no está permitido")
        require_text(requirement.get("owner"), f"{label}.owner")
        require_text(requirement.get("reference"), f"{label}.reference")

    return len(records)


def parse_arguments(argv: Sequence[str]) -> argparse.Namespace:
    default_schema = Path(__file__).resolve().parent.parent / "schemas" / "test-data.schema.json"
    parser = argparse.ArgumentParser(
        description="Valida estáticamente test-data.json y sus reglas sintéticas."
    )
    parser.add_argument("data_file", type=Path, help="Ruta al test-data.json")
    parser.add_argument(
        "--schema",
        type=Path,
        default=default_schema,
        help="Ruta al schema; por defecto usa schemas/test-data.schema.json",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str]) -> int:
    try:
        arguments = parse_arguments(argv)
        data = load_json_object(arguments.data_file, "archivo de datos")
        schema = load_json_object(arguments.schema, "schema")
        count = validate_contract(data, schema)
        print(f"VALID: story={data['story']} cases={len(data['cases'])} records={count}")
        return 0
    except ValidationError as error:
        print(f"INVALID: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
