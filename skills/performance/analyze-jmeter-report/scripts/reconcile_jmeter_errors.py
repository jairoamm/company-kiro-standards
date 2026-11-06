#!/usr/bin/env python3
"""Reconcile failed samples in a CSV JTL with JMeter statistics.json."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Mapping, Sequence


class ValidationError(ValueError):
    """Raised when local JMeter evidence cannot be reconciled."""


def require_regular_file(path: Path, label: str) -> None:
    if path.is_symlink():
        raise ValidationError(f"{label} no puede ser un symlink: {path}")
    if not path.is_file():
        raise ValidationError(f"{label} debe ser un archivo existente: {path}")


def load_statistics(path: Path) -> Mapping[str, Any]:
    require_regular_file(path, "statistics.json")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except OSError as error:
        raise ValidationError(f"no se pudo leer statistics.json: {error}") from error
    except json.JSONDecodeError as error:
        raise ValidationError(f"statistics.json inválido: {error}") from error
    if not isinstance(value, dict):
        raise ValidationError("statistics.json debe tener un objeto como raíz")
    return value


def count_jtl_failures(path: Path) -> tuple[int, Counter[str]]:
    require_regular_file(path, "JTL")
    try:
        with path.open(newline="", encoding="utf-8") as stream:
            reader = csv.DictReader(stream)
            if reader.fieldnames is None:
                raise ValidationError("el JTL CSV no contiene cabecera")
            required = {"success", "label"}
            missing = sorted(required - set(reader.fieldnames))
            if missing:
                raise ValidationError(
                    "el JTL CSV omite columnas obligatorias: " + ", ".join(missing)
                )
            samples = 0
            failures: Counter[str] = Counter()
            for row_number, row in enumerate(reader, start=2):
                success = (row.get("success") or "").strip().casefold()
                label = (row.get("label") or "").strip()
                if success not in {"true", "false"}:
                    raise ValidationError(
                        f"JTL fila {row_number}: success debe ser true o false"
                    )
                if not label:
                    raise ValidationError(f"JTL fila {row_number}: label está vacío")
                samples += 1
                if success == "false":
                    failures[label] += 1
    except OSError as error:
        raise ValidationError(f"no se pudo leer el JTL: {error}") from error
    if samples == 0:
        raise ValidationError("el JTL CSV no contiene muestras")
    return samples, failures


def total_statistics_errors(statistics: Mapping[str, Any]) -> tuple[int, int]:
    total = statistics.get("Total")
    if not isinstance(total, dict):
        raise ValidationError("statistics.json no contiene un objeto Total")
    sample_count = total.get("sampleCount")
    error_count = total.get("errorCount")
    if not isinstance(sample_count, int) or isinstance(sample_count, bool) or sample_count < 0:
        raise ValidationError("Total.sampleCount debe ser un entero no negativo")
    if not isinstance(error_count, int) or isinstance(error_count, bool) or error_count < 0:
        raise ValidationError("Total.errorCount debe ser un entero no negativo")
    if error_count > sample_count:
        raise ValidationError("Total.errorCount no puede superar Total.sampleCount")
    return sample_count, error_count


def parse_arguments(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Compara success=false de un JTL CSV con sampleCount y errorCount "
            "de statistics.json, sin ejecutar JMeter."
        )
    )
    parser.add_argument("--jtl", required=True, type=Path, help="Ruta al results.jtl CSV")
    parser.add_argument(
        "--statistics",
        required=True,
        type=Path,
        help="Ruta al statistics.json del dashboard",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str]) -> int:
    try:
        arguments = parse_arguments(argv)
        jtl_samples, failures_by_label = count_jtl_failures(arguments.jtl)
        statistics = load_statistics(arguments.statistics)
        statistics_samples, statistics_errors = total_statistics_errors(statistics)
        jtl_errors = sum(failures_by_label.values())
        status = (
            "MATCH"
            if jtl_samples == statistics_samples and jtl_errors == statistics_errors
            else "MISMATCH"
        )
        result = {
            "status": status,
            "jtl": {
                "sampleCount": jtl_samples,
                "errorCount": jtl_errors,
                "errorsByLabel": dict(sorted(failures_by_label.items())),
            },
            "statistics": {
                "sampleCount": statistics_samples,
                "errorCount": statistics_errors,
            },
        }
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
        return 0 if status == "MATCH" else 1
    except ValidationError as error:
        print(f"INVALID: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
