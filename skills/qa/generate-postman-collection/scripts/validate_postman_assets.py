#!/usr/bin/env python3
"""Validate Postman collection and environment files without running Newman."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Iterator, Mapping, Sequence
from urllib.parse import urlparse


COLLECTION_SCHEMA = "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
SENSITIVE_KEY_PARTS = ("token", "secret", "cookie", "authorization", "credential")


class ValidationError(ValueError):
    """Raised when a Postman asset is invalid or unsafe to version."""


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


def iter_requests(items: Any, location: str = "item") -> Iterator[tuple[str, Mapping[str, Any]]]:
    if not isinstance(items, list):
        raise ValidationError(f"{location} debe ser una lista")
    for index, item in enumerate(items):
        item_location = f"{location}[{index}]"
        if not isinstance(item, dict):
            raise ValidationError(f"{item_location} debe ser un objeto")
        nested = item.get("item")
        request = item.get("request")
        if nested is not None:
            yield from iter_requests(nested, f"{item_location}.item")
        elif isinstance(request, dict):
            yield item_location, request
        else:
            raise ValidationError(f"{item_location} debe contener item o request")


def validate_request_url(raw_url: str, location: str) -> None:
    if "{{BASE_URL}}" in raw_url:
        return
    parsed = urlparse(raw_url)
    if parsed.scheme in {"http", "https"} and parsed.hostname:
        if parsed.hostname.casefold().endswith(".test"):
            return
    raise ValidationError(
        f"{location} debe usar {{{{BASE_URL}}}} o un dominio sintético .test"
    )


def validate_collection(collection: Mapping[str, Any]) -> int:
    info = collection.get("info")
    if not isinstance(info, dict):
        raise ValidationError("collection.info debe ser un objeto")
    if info.get("schema") != COLLECTION_SCHEMA:
        raise ValidationError("la colección debe declarar Postman Collection v2.1")
    name = info.get("name")
    description = info.get("description")
    if not isinstance(name, str) or not name.strip():
        raise ValidationError("collection.info.name debe ser un texto no vacío")
    if not isinstance(description, str) or "Karate" not in description:
        raise ValidationError("la descripción debe conservar la regresión en Karate")

    request_count = 0
    for location, request in iter_requests(collection.get("item")):
        request_count += 1
        method = request.get("method")
        if not isinstance(method, str) or not method.strip():
            raise ValidationError(f"{location}.request.method debe ser un texto no vacío")

        raw_url_value = request.get("url")
        if isinstance(raw_url_value, str):
            raw_url = raw_url_value
        elif isinstance(raw_url_value, dict):
            raw_url = raw_url_value.get("raw")
        else:
            raw_url = None
        if not isinstance(raw_url, str) or not raw_url:
            raise ValidationError(f"{location}.request.url.raw debe ser un texto no vacío")
        validate_request_url(raw_url, f"{location}.request.url.raw")

        headers = request.get("header", [])
        if not isinstance(headers, list):
            raise ValidationError(f"{location}.request.header debe ser una lista")
        for header_index, header in enumerate(headers):
            if not isinstance(header, dict):
                raise ValidationError(
                    f"{location}.request.header[{header_index}] debe ser un objeto"
                )
            key = str(header.get("key", "")).casefold()
            value = str(header.get("value", ""))
            if any(part in key for part in SENSITIVE_KEY_PARTS):
                if value not in {"", "NO_SUMINISTRADO"} and not (
                    value.startswith("{{") and value.endswith("}}")
                ):
                    raise ValidationError(
                        f"{location}.request.header[{header_index}] contiene material sensible literal"
                    )

        body = request.get("body")
        if isinstance(body, dict) and body.get("mode") == "raw":
            raw_body = body.get("raw")
            if not isinstance(raw_body, str):
                raise ValidationError(f"{location}.request.body.raw debe ser texto")
            options = body.get("options")
            language = None
            if isinstance(options, dict) and isinstance(options.get("raw"), dict):
                language = options["raw"].get("language")
            if language == "json":
                try:
                    json.loads(raw_body)
                except json.JSONDecodeError as error:
                    raise ValidationError(
                        f"{location}.request.body.raw no contiene JSON válido: {error}"
                    ) from error
            if "@" in raw_body and ".test" not in raw_body:
                raise ValidationError(f"{location}.request.body.raw contiene un correo fuera de .test")

    if request_count == 0:
        raise ValidationError("la colección debe contener al menos un request")
    return request_count


def validate_environment(environment: Mapping[str, Any]) -> int:
    if environment.get("_postman_variable_scope") != "environment":
        raise ValidationError("el archivo environment debe declarar su scope")
    values = environment.get("values")
    if not isinstance(values, list) or not values:
        raise ValidationError("environment.values debe ser una lista no vacía")

    seen: set[str] = set()
    has_base_url = False
    for index, entry in enumerate(values):
        label = f"environment.values[{index}]"
        if not isinstance(entry, dict):
            raise ValidationError(f"{label} debe ser un objeto")
        key = entry.get("key")
        value = entry.get("value")
        if not isinstance(key, str) or not key:
            raise ValidationError(f"{label}.key debe ser un texto no vacío")
        if key in seen:
            raise ValidationError(f"variable duplicada en environment: {key}")
        seen.add(key)
        if not isinstance(value, str):
            raise ValidationError(f"{label}.value debe ser texto")
        if key == "BASE_URL":
            has_base_url = True
            if value != "NO_SUMINISTRADO":
                parsed = urlparse(value)
                if parsed.scheme not in {"http", "https"} or not parsed.hostname:
                    raise ValidationError("BASE_URL debe ser NO_SUMINISTRADO o una URL válida")
                if not parsed.hostname.casefold().endswith(".test"):
                    raise ValidationError("la plantilla BASE_URL solo puede usar un dominio .test")
        if any(part in key.casefold() for part in SENSITIVE_KEY_PARTS):
            if value not in {"", "NO_SUMINISTRADO"}:
                raise ValidationError(f"{label} contiene un valor sensible literal")

    if not has_base_url:
        raise ValidationError("el environment debe declarar BASE_URL")
    return len(values)


def parse_arguments(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Valida JSON y límites seguros de una colección Postman sin ejecutar Newman."
    )
    parser.add_argument(
        "--collection", required=True, type=Path, help="Ruta a la colección Postman v2.1"
    )
    parser.add_argument(
        "--environment", required=True, type=Path, help="Ruta al environment de plantilla"
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str]) -> int:
    try:
        arguments = parse_arguments(argv)
        collection = load_json_object(arguments.collection, "colección")
        environment = load_json_object(arguments.environment, "environment")
        request_count = validate_collection(collection)
        variable_count = validate_environment(environment)
        print(f"VALID: requests={request_count} environmentVariables={variable_count}")
        return 0
    except ValidationError as error:
        print(f"INVALID: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
