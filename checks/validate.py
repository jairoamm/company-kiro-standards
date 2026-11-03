#!/usr/bin/env python3
"""Validate the repository without executing any Skill content."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path, PurePosixPath
from typing import Any, Dict, List, Mapping, Set


ROOT = Path(__file__).resolve().parent.parent
ALLOWED_TOP_LEVEL = {
    ".git",
    ".github",
    ".gitignore",
    "README.md",
    "CHANGELOG.md",
    "CONTRIBUTING.md",
    "SECURITY.md",
    "catalog.json",
    "steering",
    "skills",
    "profiles",
    "bundles",
    "tools",
    "checks",
    "docs",
}
REQUIRED_FILES = {
    "README.md",
    "CHANGELOG.md",
    "CONTRIBUTING.md",
    "SECURITY.md",
    "catalog.json",
    "bundles/common.json",
    "bundles/developer.json",
    "bundles/qa.json",
    "tools/sync.py",
    "tools/sync.sh",
    "tools/sync.ps1",
    "docs/architecture.md",
    "docs/adoption.md",
    "docs/governance.md",
    "docs/demo-runbook.md",
    "docs/scopes-and-profiles.md",
    "profiles/development/steering/dev-bug-resolution.md",
    "profiles/qa/steering/qa-bug-investigation.md",
}
SECRET_PATTERNS = {
    "private key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "AWS access key": re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b"),
    "GitHub token": re.compile(r"\bgh[opsu]_[A-Za-z0-9]{30,}\b"),
    "literal password": re.compile(
        r"(?i)\bpassword\s*[:=]\s*[\"'][^\"'${}<]{8,}[\"']"
    ),
    "literal token": re.compile(
        r"(?i)\b(?:api[_-]?key|access[_-]?token)\s*[:=]\s*[\"'][^\"'${}<]{12,}[\"']"
    ),
}
DANGEROUS_PATTERNS = {
    "recursive root deletion": re.compile(r"\brm\s+-[^\n]*r[^\n]*f[^\n]*\s+/(?:\s|$)"),
    "remote pipe to shell": re.compile(r"(?i)\b(?:curl|wget)\b[^\n|]*\|\s*(?:ba|z|k)?sh\b"),
    "PowerShell expression execution": re.compile(r"(?i)\bInvoke-Expression\b"),
    "force push": re.compile(r"\bgit\s+push\b[^\n]*--force(?:-with-lease)?\b"),
}
PERSONAL_PATH_PATTERNS = {
    "macOS personal path": re.compile(r"/Users/[^/<\s]+/"),
    "Windows personal path": re.compile(r"[A-Za-z]:\\Users\\[^\\<\s]+\\"),
}
TEXT_SUFFIXES = {".md", ".json", ".py", ".sh", ".ps1", ".txt", ".yaml", ".yml"}
REQUIRED_ROLE_ASSETS: Mapping[str, Set[str]] = {
    "developer": {
        "steering-development-ui-testability",
        "skill-prepare-qa-handoff",
        "skill-test-plan-traceability",
    },
    "qa": {
        "steering-qa-black-box-test-automation",
        "skill-generate-selenium-tests",
        "skill-test-plan-traceability",
        "skill-generate-jmeter-project",
        "skill-create-performance-plan",
        "skill-analyze-jmeter-report",
    },
}
FORBIDDEN_ROLE_ASSETS: Mapping[str, Set[str]] = {
    "developer": {
        "steering-qa-test-automation-standards",
        "steering-qa-black-box-test-automation",
        "skill-generate-selenium-tests",
        "skill-generate-jmeter-project",
        "skill-create-performance-plan",
        "skill-analyze-jmeter-report",
    },
    "qa": {
        "steering-development-standards",
        "steering-development-ui-testability",
        "skill-prepare-qa-handoff",
    },
}
PROFILE_FILES: Mapping[str, Path] = {
    "development": Path("profiles/development/steering/dev-bug-resolution.md"),
    "qa": Path("profiles/qa/steering/qa-bug-investigation.md"),
}
PROFILE_REQUIRED_SNIPPETS: Mapping[str, Set[str]] = {
    "development": {
        "bug-diagnosis.md",
        "bugfix spec",
        "prueba de regresión",
        "prueba roja",
        "cambio mínimo",
        "gates",
        "reconcilia las specs",
        ".kiro/specs/<bug>/{bugfix,design,tasks}.md",
        "draft — no aprobado",
        "no concede permisos",
    },
    "qa": {
        "inspeccionar",
        "reproducir",
        "diagnosticar",
        "documenta",
        "bug-diagnosis.md",
        "dev-intake.md",
        "no edites código productivo",
        "no crees, cambies ni elimines pruebas",
        "no cambies dependencias",
        "no implementes la corrección",
        "no incluyas la corrección en un commit",
        "acceso remoto de solo lectura",
        ".kiro/specs/<bug>/{bugfix,design,tasks}.md",
        "draft — no aprobado",
        "no concede permisos",
    },
}


class Validator:
    def __init__(self) -> None:
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def error(self, message: str) -> None:
        self.errors.append(message)

    def warning(self, message: str) -> None:
        self.warnings.append(message)


def load_json(path: Path, validator: Validator) -> Mapping[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        validator.error(f"Missing JSON file: {path.relative_to(ROOT)}")
        return {}
    except json.JSONDecodeError as error:
        validator.error(f"Invalid JSON in {path.relative_to(ROOT)}: {error}")
        return {}
    if not isinstance(value, dict):
        validator.error(f"JSON root must be an object: {path.relative_to(ROOT)}")
        return {}
    return value


def safe_relative(raw: Any, label: str, validator: Validator) -> PurePosixPath | None:
    if not isinstance(raw, str) or not raw.strip():
        validator.error(f"{label} must be a non-empty string")
        return None
    if "\\" in raw:
        validator.error(f"{label} must use forward slashes: {raw}")
        return None
    path = PurePosixPath(raw)
    if path.is_absolute() or path == PurePosixPath(".") or ".." in path.parts:
        validator.error(f"Unsafe {label}: {raw}")
        return None
    return path


def validate_root(validator: Validator) -> None:
    for required in sorted(REQUIRED_FILES):
        if not (ROOT / required).is_file():
            validator.error(f"Required file is missing: {required}")

    for child in ROOT.iterdir():
        if child.name not in ALLOWED_TOP_LEVEL:
            validator.error(f"Unexpected top-level entry: {child.name}")

    for path in ROOT.rglob("*"):
        if path.is_symlink():
            validator.error(f"Symlinks are not allowed: {path.relative_to(ROOT)}")


def parse_frontmatter(path: Path, validator: Validator) -> Mapping[str, str]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        validator.error(f"Missing frontmatter: {path.relative_to(ROOT)}")
        return {}
    try:
        closing = lines[1:].index("---") + 1
    except ValueError:
        validator.error(f"Unclosed frontmatter: {path.relative_to(ROOT)}")
        return {}

    result: Dict[str, str] = {}
    for line in lines[1:closing]:
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            validator.error(f"Invalid frontmatter line in {path.relative_to(ROOT)}: {line}")
            continue
        key, value = line.split(":", 1)
        result[key.strip()] = value.strip()
    return result


def validate_catalog(validator: Validator) -> tuple[str, Mapping[str, Mapping[str, Any]]]:
    catalog = load_json(ROOT / "catalog.json", validator)
    version = catalog.get("version")
    if not isinstance(version, str) or not re.fullmatch(r"\d+\.\d+\.\d+", version):
        validator.error("catalog.json version must use semantic versioning")
        version = ""

    raw_assets = catalog.get("assets")
    if not isinstance(raw_assets, list):
        validator.error("catalog.json assets must be an array")
        return version, {}

    assets: Dict[str, Mapping[str, Any]] = {}
    targets: Set[str] = set()
    for index, raw_asset in enumerate(raw_assets):
        if not isinstance(raw_asset, dict):
            validator.error(f"Catalog asset #{index + 1} must be an object")
            continue
        asset_id = raw_asset.get("id")
        if not isinstance(asset_id, str) or not re.fullmatch(r"[a-z0-9-]+", asset_id):
            validator.error(f"Catalog asset #{index + 1} has an invalid id")
            continue
        if asset_id in assets:
            validator.error(f"Duplicate catalog asset id: {asset_id}")
            continue
        assets[asset_id] = raw_asset

        kind = raw_asset.get("kind")
        if kind not in {"steering", "skill"}:
            validator.error(f"Unsupported kind for {asset_id}: {kind}")
        if raw_asset.get("status") not in {"draft", "approved", "deprecated"}:
            validator.error(f"Invalid status for {asset_id}: {raw_asset.get('status')}")
        if not isinstance(raw_asset.get("owner"), str) or not raw_asset.get("owner"):
            validator.error(f"Missing owner for {asset_id}")

        source = safe_relative(raw_asset.get("source"), f"source for {asset_id}", validator)
        target = safe_relative(raw_asset.get("target"), f"target for {asset_id}", validator)
        if source is None or target is None:
            continue

        source_path = ROOT.joinpath(*source.parts)
        if not source_path.is_file() or source_path.is_symlink():
            validator.error(f"Missing or unsafe source for {asset_id}: {source}")

        expected_source_prefix = "steering" if kind == "steering" else "skills"
        expected_target_prefix = "steering" if kind == "steering" else "skills"
        if source.parts[0] != expected_source_prefix:
            validator.error(f"Source for {asset_id} must be under {expected_source_prefix}/")
        if target.parts[0] != expected_target_prefix:
            validator.error(f"Target for {asset_id} must be under {expected_target_prefix}/")
        if target.as_posix() in targets:
            validator.error(f"Duplicate catalog target: {target}")
        targets.add(target.as_posix())

        if source_path.is_file() and kind == "skill":
            frontmatter = parse_frontmatter(source_path, validator)
            if frontmatter.get("name") != raw_asset.get("name"):
                validator.error(f"Skill name mismatch for {asset_id}")
            if len(frontmatter.get("description", "")) < 20:
                validator.error(f"Skill description is too short for {asset_id}")
        elif source_path.is_file() and kind == "steering":
            frontmatter = parse_frontmatter(source_path, validator)
            if frontmatter.get("inclusion") not in {"always", "auto", "manual", "fileMatch"}:
                validator.error(f"Invalid Steering inclusion for {asset_id}")

    return version, assets


def validate_profiles(
    assets: Mapping[str, Mapping[str, Any]], validator: Validator
) -> None:
    inclusions: Dict[str, str] = {}
    profile_markers = {
        marker
        for path in PROFILE_FILES.values()
        for marker in {path.as_posix(), path.stem}
    }

    for role, relative in PROFILE_FILES.items():
        path = ROOT / relative
        if not path.is_file():
            continue

        frontmatter = parse_frontmatter(path, validator)
        inclusion = frontmatter.get("inclusion", "")
        if inclusion not in {"auto", "manual"}:
            validator.error(
                f"Profile {role} must use auto or manual inclusion: {relative}"
            )
        else:
            inclusions[role] = inclusion
        if frontmatter.get("name") != path.stem:
            validator.error(f"Profile name must match filename: {relative}")
        if len(frontmatter.get("description", "")) < 40:
            validator.error(f"Profile description is too short: {relative}")

        text = path.read_text(encoding="utf-8").casefold()
        missing = sorted(
            snippet
            for snippet in PROFILE_REQUIRED_SNIPPETS[role]
            if snippet.casefold() not in text
        )
        if missing:
            validator.error(
                f"Profile {role} is missing required boundaries: " + ", ".join(missing)
            )

    if len(inclusions) == len(PROFILE_FILES) and all(
        inclusion == "auto" for inclusion in inclusions.values()
    ):
        validator.error(
            "Development and QA profiles cannot both use auto inclusion because "
            "their bugfix responsibilities conflict"
        )

    for asset_id, asset in assets.items():
        source = asset.get("source")
        if isinstance(source, str) and source.startswith("profiles/"):
            validator.error(
                f"Personal profile must not be a catalog asset: {asset_id} ({source})"
            )

    for bundle_path in sorted((ROOT / "bundles").glob("*.json")):
        text = bundle_path.read_text(encoding="utf-8")
        included_markers = sorted(marker for marker in profile_markers if marker in text)
        if included_markers:
            validator.error(
                f"Bundle {bundle_path.stem} references personal profile content: "
                + ", ".join(included_markers)
            )


def validate_bundles(
    version: str, assets: Mapping[str, Mapping[str, Any]], validator: Validator
) -> None:
    bundles: Dict[str, Mapping[str, Any]] = {}
    for path in sorted((ROOT / "bundles").glob("*.json")):
        bundle = load_json(path, validator)
        name = path.stem
        bundles[name] = bundle
        if bundle.get("name") != name:
            validator.error(f"Bundle filename/name mismatch: {name}")
        if bundle.get("version") != version:
            validator.error(f"Bundle/catalog version mismatch: {name}")
        extends = bundle.get("extends")
        asset_ids = bundle.get("assets")
        if not isinstance(extends, list) or not all(isinstance(item, str) for item in extends):
            validator.error(f"Bundle {name} has invalid extends")
        if not isinstance(asset_ids, list) or not all(isinstance(item, str) for item in asset_ids):
            validator.error(f"Bundle {name} has invalid assets")
        elif len(asset_ids) != len(set(asset_ids)):
            validator.error(f"Bundle {name} contains duplicate asset ids")

    used_assets: Set[str] = set()

    def resolve(name: str, active: Set[str]) -> List[str]:
        if name in active:
            validator.error(f"Bundle inheritance cycle detected at: {name}")
            return []
        bundle = bundles.get(name)
        if bundle is None:
            validator.error(f"Unknown inherited bundle: {name}")
            return []
        active.add(name)
        result: List[str] = []
        extends = bundle.get("extends", [])
        if isinstance(extends, list):
            for parent in extends:
                if isinstance(parent, str):
                    result.extend(resolve(parent, active))
        asset_ids = bundle.get("assets", [])
        if isinstance(asset_ids, list):
            for asset_id in asset_ids:
                if not isinstance(asset_id, str):
                    continue
                if asset_id not in assets:
                    validator.error(f"Bundle {name} references unknown asset: {asset_id}")
                else:
                    result.append(asset_id)
                    used_assets.add(asset_id)
        active.remove(name)
        return result

    resolved_by_bundle: Dict[str, Set[str]] = {}
    for name in sorted(bundles):
        resolved = resolve(name, set())
        resolved_by_bundle[name] = set(resolved)
        if len(resolved) != len(set(resolved)):
            validator.error(f"Bundle {name} resolves duplicate assets through inheritance")

    for name, required in REQUIRED_ROLE_ASSETS.items():
        missing = sorted(required - resolved_by_bundle.get(name, set()))
        if missing:
            validator.error(
                f"Bundle {name} is missing required role assets: " + ", ".join(missing)
            )

    for name, forbidden in FORBIDDEN_ROLE_ASSETS.items():
        unexpected = sorted(forbidden & resolved_by_bundle.get(name, set()))
        if unexpected:
            validator.error(
                f"Bundle {name} contains assets owned by another role: "
                + ", ".join(unexpected)
            )

    unused = sorted(set(assets) - used_assets)
    if unused:
        validator.warning("Catalog assets not included in a bundle: " + ", ".join(unused))


def validate_text_content(validator: Validator) -> None:
    excluded_prefixes = {Path(".git"), Path("checks")}
    for path in ROOT.rglob("*"):
        if not path.is_file() or path.is_symlink() or path.suffix not in TEXT_SUFFIXES:
            continue
        relative = path.relative_to(ROOT)
        if any(relative == prefix or prefix in relative.parents for prefix in excluded_prefixes):
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for label, pattern in SECRET_PATTERNS.items():
            if pattern.search(text):
                validator.error(f"Possible {label} in {relative}")
        for label, pattern in PERSONAL_PATH_PATTERNS.items():
            if pattern.search(text):
                validator.error(f"Possible {label} in {relative}")
        if relative.parts and relative.parts[0] in {"skills", "steering", "profiles"}:
            for label, pattern in DANGEROUS_PATTERNS.items():
                if pattern.search(text):
                    validator.error(f"Dangerous instruction ({label}) in {relative}")


def main() -> int:
    validator = Validator()
    validate_root(validator)
    version, assets = validate_catalog(validator)
    validate_profiles(assets, validator)
    validate_bundles(version, assets, validator)
    validate_text_content(validator)

    for warning in validator.warnings:
        print(f"WARNING: {warning}")
    for error in validator.errors:
        print(f"ERROR: {error}", file=sys.stderr)

    if validator.errors:
        print(
            f"Validation failed with {len(validator.errors)} error(s) "
            f"and {len(validator.warnings)} warning(s).",
            file=sys.stderr,
        )
        return 1

    print(
        f"Validation passed: {len(assets)} catalog assets, "
        f"{len(list((ROOT / 'bundles').glob('*.json')))} bundles, "
        f"{len(validator.warnings)} warning(s)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
