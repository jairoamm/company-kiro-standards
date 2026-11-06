#!/usr/bin/env python3
"""Validate a ui-selectors.json file without browser or network access."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence


class ValidationError(ValueError):
    """Raised when a file or selector contract is invalid."""


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


def require_non_empty_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"{label} debe ser un texto no vacío")
    return value


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

    require_exact_keys(data, set(required), set(properties), "contrato")

    expected_schema_version = properties.get("schemaVersion", {}).get("const")
    if data.get("schemaVersion") != expected_schema_version:
        raise ValidationError(
            f"schemaVersion debe ser {expected_schema_version!r}"
        )

    version_pattern = properties.get("contractVersion", {}).get("pattern")
    story_pattern = properties.get("historia", {}).get("pattern")
    if not isinstance(version_pattern, str) or not isinstance(story_pattern, str):
        raise ValidationError("el schema omite patrones de versión o historia")

    contract_version = require_non_empty_string(
        data.get("contractVersion"), "contractVersion"
    )
    story = require_non_empty_string(data.get("historia"), "historia")
    if re.fullmatch(version_pattern, contract_version) is None:
        raise ValidationError("contractVersion debe usar versionamiento semántico")
    if re.fullmatch(story_pattern, story) is None:
        raise ValidationError("historia no cumple el patrón publicado")

    selector_schema = definitions.get("selector")
    case_schema = definitions.get("caseId")
    if not isinstance(selector_schema, dict) or not isinstance(case_schema, dict):
        raise ValidationError("el schema omite las definiciones selector o caseId")

    selector_properties = selector_schema.get("properties")
    selector_required = selector_schema.get("required")
    case_pattern = case_schema.get("pattern")
    if not isinstance(selector_properties, dict) or not isinstance(selector_required, list):
        raise ValidationError("la definición selector del schema es inválida")
    if not isinstance(case_pattern, str):
        raise ValidationError("la definición caseId del schema es inválida")

    strategy_values = selector_properties.get("estrategia", {}).get("enum")
    if not isinstance(strategy_values, list) or not all(
        isinstance(item, str) for item in strategy_values
    ):
        raise ValidationError("el schema no declara estrategias válidas")
    strategies = set(strategy_values)

    selectors = data.get("selectors")
    if not isinstance(selectors, list) or not selectors:
        raise ValidationError("selectors debe ser una lista no vacía")

    names: set[str] = set()
    name_pattern = selector_properties.get("nombre", {}).get("pattern")
    if not isinstance(name_pattern, str):
        raise ValidationError("el schema no declara el patrón de nombre")

    for index, raw_selector in enumerate(selectors):
        label = f"selectors[{index}]"
        if not isinstance(raw_selector, dict):
            raise ValidationError(f"{label} debe ser un objeto")
        require_exact_keys(
            raw_selector,
            set(selector_required),
            set(selector_properties),
            label,
        )

        name = require_non_empty_string(raw_selector.get("nombre"), f"{label}.nombre")
        if re.fullmatch(name_pattern, name) is None:
            raise ValidationError(f"{label}.nombre no cumple el patrón publicado")
        if name in names:
            raise ValidationError(f"nombre de selector duplicado: {name}")
        names.add(name)

        for field in ("pantalla", "estado", "valor"):
            require_non_empty_string(raw_selector.get(field), f"{label}.{field}")

        strategy = raw_selector.get("estrategia")
        if strategy not in strategies:
            raise ValidationError(f"{label}.estrategia no está permitida: {strategy!r}")
        if strategy == "role":
            require_non_empty_string(
                raw_selector.get("nombreAccesible"),
                f"{label}.nombreAccesible",
            )
        elif "nombreAccesible" in raw_selector:
            require_non_empty_string(
                raw_selector.get("nombreAccesible"),
                f"{label}.nombreAccesible",
            )

        cases = raw_selector.get("casosRelacionados")
        if not isinstance(cases, list) or not cases:
            raise ValidationError(f"{label}.casosRelacionados debe ser una lista no vacía")
        if len(cases) != len(set(cases)):
            raise ValidationError(f"{label}.casosRelacionados contiene duplicados")
        for case in cases:
            if not isinstance(case, str) or re.fullmatch(case_pattern, case) is None:
                raise ValidationError(f"{label} contiene un identificador de caso inválido")

    return len(selectors)


def parse_arguments(argv: Sequence[str]) -> argparse.Namespace:
    default_schema = Path(__file__).resolve().parent.parent / "schemas" / "ui-selectors.schema.json"
    parser = argparse.ArgumentParser(
        description="Valida estáticamente ui-selectors.json contra el contrato publicado."
    )
    parser.add_argument("selectors_file", type=Path, help="Ruta al ui-selectors.json")
    parser.add_argument(
        "--schema",
        type=Path,
        default=default_schema,
        help="Ruta al schema; por defecto usa schemas/ui-selectors.schema.json",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str]) -> int:
    try:
        arguments = parse_arguments(argv)
        data = load_json_object(arguments.selectors_file, "archivo de selectores")
        schema = load_json_object(arguments.schema, "schema")
        count = validate_contract(data, schema)
        print(
            "VALID: "
            f"story={data['historia']} contractVersion={data['contractVersion']} "
            f"selectors={count}"
        )
        return 0
    except ValidationError as error:
        print(f"INVALID: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
