#!/usr/bin/env python3
"""Validate repository content and run allowlisted local support checks."""

from __future__ import annotations

import ast
import csv
import json
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path, PurePosixPath
from typing import Any, Dict, List, Mapping, Set
from urllib.parse import unquote, urlsplit


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
FORBIDDEN_SKILL_CLAIMS = {
    "claims that the Skill executes tests": re.compile(
        r"(?im)^\s*(?:[-*]\s+)?(?:esta|este|la|el|una)\s+skill\s+"
        r"(?:(?:debe|puede|va\s+a)\s+)?(?:ejecuta|ejecutar|ejecutará|corre|correr|lanza|lanzar)\b"
    ),
    "claims that the Skill certifies results": re.compile(
        r"(?im)^\s*(?:[-*]\s+)?(?:esta|este|la|el|una)\s+skill\s+"
        r"(?:(?:debe|puede|va\s+a)\s+)?(?:certifica|certificar|certificará)\b"
    ),
    "instructs secret persistence": re.compile(
        r"(?im)^\s*(?:[-*]|\d+\.)?\s*"
        r"(?:almacena|guardar?|guarda|persiste|persistir)\s+"
        r"(?:los?\s+|las?\s+)?(?:secretos?|tokens?|contraseñas?|credenciales?)\b"
    ),
}
REQUIRED_SKILL_SECTIONS = (
    "Propósito",
    "Cuándo usarla",
    "Políticas relacionadas",
    "Entradas obligatorias",
    "Precondiciones y bloqueos",
    "Procedimiento",
    "Archivos de salida",
    "Ejemplo de prompt",
    "Ejemplo de salida",
    "Validación",
    "Manejo de fallos",
    "Límites y responsabilidades",
)
SKILLS_REQUIRING_NEGATIVE_SCOPE = {
    "prepare-synthetic-test-data",
    "test-plan-traceability",
}
SKILL_REQUIRED_SNIPPETS: Mapping[str, Set[str]] = {
    "prepare-synthetic-test-data": {
        "qa es dueño del archivo",
        "kiro propone un borrador",
        "no copia ni anonimiza datos reales",
        "no inventa estados de backend",
        "dev o plataforma",
        "no ejecuta pruebas",
        "no certifica",
        "qa-input/<hu>/test-data.json",
        "revisión humana obligatoria",
    },
    "generate-postman-collection": {
        "exploración",
        "reproducción rápida",
        "karate conserva la regresión versionada",
        "postman no ejecuta la colección",
        "postman/credential-recovery.postman_collection.json",
        "build/postman/junit.xml",
        "build/postman/report.html",
    },
}
PERSONAL_PATH_PATTERNS = {
    "macOS personal path": re.compile(r"/Users/[^/<\s]+/"),
    "Windows personal path": re.compile(r"[A-Za-z]:\\Users\\[^\\<\s]+\\"),
}
TEXT_SUFFIXES = {
    ".csv",
    ".feature",
    ".java",
    ".jmx",
    ".js",
    ".json",
    ".jtl",
    ".md",
    ".properties",
    ".ps1",
    ".py",
    ".sh",
    ".template",
    ".txt",
    ".xml",
    ".yaml",
    ".yml",
}
SKILL_SUPPORT_DIRECTORIES = {"examples", "templates", "schemas", "scripts", "references"}
MARKDOWN_LINK_PATTERN = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
SAFE_SKILL_SMOKE_TESTS = (
    (
        "skills/qa/generate-selenium-tests/scripts/validate_ui_selectors.py",
        "skills/qa/generate-selenium-tests/examples/ui-selectors.json",
        "--schema",
        "skills/qa/generate-selenium-tests/schemas/ui-selectors.schema.json",
    ),
    (
        "skills/qa/prepare-synthetic-test-data/scripts/validate_test_data.py",
        "skills/qa/prepare-synthetic-test-data/examples/test-data.json",
        "--schema",
        "skills/qa/prepare-synthetic-test-data/schemas/test-data.schema.json",
    ),
    (
        "skills/qa/generate-postman-collection/scripts/validate_postman_assets.py",
        "--collection",
        "skills/qa/generate-postman-collection/examples/credential-recovery.postman_collection.json",
        "--environment",
        "skills/qa/generate-postman-collection/templates/local.postman_environment.json",
    ),
    (
        "skills/performance/analyze-jmeter-report/scripts/reconcile_jmeter_errors.py",
        "--jtl",
        "skills/performance/analyze-jmeter-report/examples/results.jtl",
        "--statistics",
        "skills/performance/analyze-jmeter-report/examples/statistics.json",
    ),
)
REQUIRED_ROLE_ASSETS: Mapping[str, Set[str]] = {
    "developer": {
        "steering-development-ui-testability",
        "skill-prepare-qa-handoff",
        "skill-test-plan-traceability",
    },
    "qa": {
        "steering-qa-black-box-test-automation",
        "skill-prepare-synthetic-test-data",
        "skill-generate-selenium-tests",
        "skill-generate-karate-tests",
        "skill-generate-postman-collection",
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
        "skill-generate-karate-tests",
        "skill-generate-postman-collection",
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


class DuplicateJsonKeyError(ValueError):
    """Raised when a JSON object repeats a key."""


def reject_duplicate_json_keys(pairs: List[tuple[str, Any]]) -> Dict[str, Any]:
    result: Dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateJsonKeyError(key)
        result[key] = value
    return result


def load_json(path: Path, validator: Validator) -> Mapping[str, Any]:
    try:
        value = json.loads(
            path.read_text(encoding="utf-8"),
            object_pairs_hook=reject_duplicate_json_keys,
        )
    except FileNotFoundError:
        validator.error(f"Missing JSON file: {path.relative_to(ROOT)}")
        return {}
    except DuplicateJsonKeyError as error:
        validator.error(
            f"Duplicate JSON key in {path.relative_to(ROOT)}: {error}"
        )
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


def markdown_section(text: str, title: str) -> str | None:
    match = re.search(
        rf"(?ms)^##\s+{re.escape(title)}\s*$\n(.*?)(?=^##\s+|\Z)",
        text,
    )
    return match.group(1).strip() if match else None


def validate_skills(
    assets: Mapping[str, Mapping[str, Any]], validator: Validator
) -> None:
    skill_paths = sorted((ROOT / "skills").glob("**/SKILL.md"))
    discovered_sources = {
        path.relative_to(ROOT).as_posix()
        for path in skill_paths
    }
    catalog_sources = {
        source
        for asset in assets.values()
        for source in [asset.get("source")]
        if asset.get("kind") == "skill" and isinstance(source, str)
    }

    for source in sorted(discovered_sources - catalog_sources):
        validator.error(f"Skill is not registered in catalog.json: {source}")
    for source in sorted(catalog_sources - discovered_sources):
        validator.error(f"Catalog Skill source is missing: {source}")

    for path in skill_paths:
        relative = path.relative_to(ROOT)
        text = path.read_text(encoding="utf-8")
        frontmatter = parse_frontmatter(path, validator)
        if frontmatter.get("name") != path.parent.name:
            validator.error(f"Skill name must match its directory: {relative}")
        if len(frontmatter.get("description", "")) < 40:
            validator.error(f"Skill description is too short: {relative}")

        for title in REQUIRED_SKILL_SECTIONS:
            occurrences = len(
                re.findall(rf"(?m)^##\s+{re.escape(title)}\s*$", text)
            )
            if occurrences != 1:
                validator.error(
                    f"Skill {relative} must contain exactly one section: {title}"
                )

        inputs = markdown_section(text, "Entradas obligatorias")
        if inputs is not None and "`" not in inputs:
            validator.error(
                f"Skill {relative} inputs must identify paths or formats"
            )

        outputs = markdown_section(text, "Archivos de salida")
        if outputs is not None and "`" not in outputs:
            validator.error(
                f"Skill {relative} outputs must identify exact or parameterized paths"
            )

        if not re.search(r"\b(?:MUST|SHOULD|MAY)\b", text):
            validator.error(
                f"Skill {relative} must use a normative keyword with an explanation"
            )

        if (
            path.parent.name in SKILLS_REQUIRING_NEGATIVE_SCOPE
            and markdown_section(text, "Lo que esta Skill no hace") is None
        ):
            validator.error(f"Skill {relative} must state what it does not do")

        required_snippets = SKILL_REQUIRED_SNIPPETS.get(path.parent.name, set())
        folded_text = text.casefold()
        missing_snippets = sorted(
            snippet
            for snippet in required_snippets
            if snippet.casefold() not in folded_text
        )
        if missing_snippets:
            validator.error(
                f"Skill {relative} is missing required boundaries: "
                + ", ".join(missing_snippets)
            )

        procedure = markdown_section(text, "Procedimiento")
        if procedure is not None:
            step_numbers = [
                int(value)
                for value in re.findall(r"(?m)^(\d+)\.\s+\S", procedure)
            ]
            if len(step_numbers) < 3:
                validator.error(
                    f"Skill {relative} must contain at least three numbered steps"
                )
            elif step_numbers != list(range(1, len(step_numbers) + 1)):
                validator.error(
                    f"Skill {relative} procedure steps must be sequential from 1"
                )

        prompt_example = markdown_section(text, "Ejemplo de prompt")
        if prompt_example is not None and "```text" not in prompt_example:
            validator.error(
                f"Skill {relative} prompt example must use a fenced text block"
            )

        output_example = markdown_section(text, "Ejemplo de salida")
        if output_example is not None and "```" not in output_example:
            validator.error(
                f"Skill {relative} output example must contain a fenced example"
            )

        validation = markdown_section(text, "Validación")
        if validation is not None and "```bash" not in validation:
            validator.error(
                f"Skill {relative} validation must contain finite shell commands"
            )

        if "no almacenes secretos" not in text.casefold():
            validator.error(
                f"Skill {relative} must explicitly forbid storing secrets"
            )

        for label, pattern in FORBIDDEN_SKILL_CLAIMS.items():
            if pattern.search(text):
                validator.error(f"Unsafe Skill statement ({label}) in {relative}")


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
        if kind == "skill":
            if source.name != "SKILL.md" or target.name != "SKILL.md":
                validator.error(f"Skill source and target must name SKILL.md: {asset_id}")
            if source.parent.name != raw_asset.get("name"):
                validator.error(f"Skill source directory/name mismatch for {asset_id}")
            if target.parent.name != raw_asset.get("name"):
                validator.error(f"Skill target directory/name mismatch for {asset_id}")
        target_key = target.as_posix().casefold()
        if target_key in targets:
            validator.error(f"Duplicate catalog target: {target}")
        targets.add(target_key)

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
    excluded_paths = {Path("checks/validate.py")}
    for path in ROOT.rglob("*"):
        if not path.is_file() or path.is_symlink() or path.suffix not in TEXT_SUFFIXES:
            continue
        relative = path.relative_to(ROOT)
        if ".git" in relative.parts or relative in excluded_paths:
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


def markdown_link_targets(text: str) -> List[str]:
    targets: List[str] = []
    for match in MARKDOWN_LINK_PATTERN.finditer(text):
        raw_target = match.group(1).strip()
        if raw_target.startswith("<") and ">" in raw_target:
            raw_target = raw_target[1 : raw_target.index(">")]
        elif " " in raw_target:
            raw_target = raw_target.split(" ", 1)[0]
        targets.append(raw_target)
    return targets


def validate_markdown_links(validator: Validator) -> None:
    repository = ROOT.resolve()
    for path in sorted(ROOT.rglob("*.md")):
        relative = path.relative_to(ROOT)
        if ".git" in relative.parts or path.is_symlink():
            continue
        text = path.read_text(encoding="utf-8")
        for raw_target in markdown_link_targets(text):
            if not raw_target or raw_target.startswith("#"):
                continue
            parsed = urlsplit(raw_target)
            if parsed.scheme or parsed.netloc:
                continue
            decoded_path = unquote(parsed.path)
            if not decoded_path:
                continue
            if decoded_path.startswith("/"):
                validator.error(f"Absolute Markdown link in {relative}: {raw_target}")
                continue
            resolved = (path.parent / decoded_path).resolve(strict=False)
            try:
                resolved.relative_to(repository)
            except ValueError:
                validator.error(f"Markdown link escapes repository in {relative}: {raw_target}")
                continue
            if not resolved.exists():
                validator.error(f"Broken Markdown link in {relative}: {raw_target}")


def validate_json_and_examples(validator: Validator) -> None:
    for path in sorted(ROOT.rglob("*.json")):
        relative = path.relative_to(ROOT)
        if ".git" in relative.parts or path.is_symlink():
            continue
        load_json(path, validator)

    for path in sorted((ROOT / "skills").glob("**/schemas/*.schema.json")):
        schema = load_json(path, validator)
        relative = path.relative_to(ROOT)
        if schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
            validator.error(f"Schema must declare draft 2020-12: {relative}")
        schema_id = schema.get("$id")
        if not isinstance(schema_id, str) or not schema_id.startswith("https://"):
            validator.error(f"Schema must declare an HTTPS $id: {relative}")
        elif not urlsplit(schema_id).hostname or not urlsplit(schema_id).hostname.endswith(
            ".test"
        ):
            validator.error(f"Schema $id must use a reserved .test domain: {relative}")
        if schema.get("type") != "object":
            validator.error(f"Schema root must describe an object: {relative}")

    for path in sorted((ROOT / "skills").glob("**/examples/*.jmx")) + sorted(
        (ROOT / "skills").glob("**/templates/*.jmx")
    ):
        try:
            ET.parse(path)
        except (ET.ParseError, OSError) as error:
            validator.error(f"Invalid XML in {path.relative_to(ROOT)}: {error}")

    for path in sorted((ROOT / "skills").glob("**/examples/*.csv")):
        try:
            with path.open(newline="", encoding="utf-8") as stream:
                reader = csv.reader(stream)
                header = next(reader, None)
                first_row = next(reader, None)
            if not header or first_row is None:
                validator.error(
                    f"CSV example must contain a header and data: {path.relative_to(ROOT)}"
                )
        except (OSError, csv.Error) as error:
            validator.error(f"Invalid CSV in {path.relative_to(ROOT)}: {error}")


def validate_skill_support(validator: Validator) -> None:
    for skill_path in sorted((ROOT / "skills").glob("**/SKILL.md")):
        skill_directory = skill_path.parent
        relative_skill = skill_path.relative_to(ROOT)
        text = skill_path.read_text(encoding="utf-8")
        links = markdown_link_targets(text)
        support_directories = []

        for child in sorted(skill_directory.iterdir()):
            if child.name == "SKILL.md":
                continue
            if not child.is_dir() or child.name not in SKILL_SUPPORT_DIRECTORIES:
                validator.error(
                    f"Unexpected Skill entry outside support folders: {child.relative_to(ROOT)}"
                )
                continue
            support_directories.append(child)

        if not support_directories:
            validator.error(f"Skill has no reusable support files: {relative_skill}")

        for support_directory in support_directories:
            files = sorted(
                path
                for path in support_directory.rglob("*")
                if path.is_file() and not path.is_symlink()
            )
            if not files:
                validator.error(
                    f"Skill support folder is empty: {support_directory.relative_to(ROOT)}"
                )
            prefix = f"{support_directory.name}/"
            if not any(target.startswith(prefix) for target in links):
                validator.error(
                    f"Skill {relative_skill} must link explicitly to {support_directory.name}/"
                )

        scripts_directory = skill_directory / "scripts"
        if not scripts_directory.is_dir():
            continue
        for script in sorted(scripts_directory.glob("*.py")):
            try:
                source = script.read_text(encoding="utf-8")
                ast.parse(source, filename=str(script))
            except (OSError, SyntaxError) as error:
                validator.error(f"Invalid Python script {script.relative_to(ROOT)}: {error}")
                continue
            if "ArgumentParser(" not in source or "if __name__ == \"__main__\"" not in source:
                validator.error(
                    f"Skill script must expose a conventional CLI: {script.relative_to(ROOT)}"
                )


def validate_no_empty_directories(validator: Validator) -> None:
    for path in sorted((ROOT / "skills").rglob("*")):
        relative = path.relative_to(ROOT)
        if not path.is_dir() or path.is_symlink():
            continue
        try:
            next(path.iterdir())
        except StopIteration:
            validator.error(f"Empty directory is not allowed: {relative}")


def run_safe_skill_smoke_tests(validator: Validator) -> None:
    for command in SAFE_SKILL_SMOKE_TESTS:
        script = ROOT / command[0]
        if not script.is_file() or script.is_symlink():
            validator.error(f"Allowlisted smoke script is missing or unsafe: {command[0]}")
            continue
        for arguments in (("--help",), command[1:]):
            try:
                completed = subprocess.run(
                    [sys.executable, str(script), *arguments],
                    cwd=ROOT,
                    capture_output=True,
                    text=True,
                    timeout=10,
                    check=False,
                )
            except (OSError, subprocess.TimeoutExpired) as error:
                validator.error(f"Smoke check could not run for {command[0]}: {error}")
                continue
            if completed.returncode != 0:
                detail = completed.stderr.strip() or completed.stdout.strip() or "no output"
                validator.error(
                    f"Smoke check failed for {command[0]} with {list(arguments)}: {detail}"
                )


def main() -> int:
    validator = Validator()
    validate_root(validator)
    version, assets = validate_catalog(validator)
    validate_skills(assets, validator)
    validate_profiles(assets, validator)
    validate_bundles(version, assets, validator)
    validate_markdown_links(validator)
    validate_json_and_examples(validator)
    validate_skill_support(validator)
    validate_no_empty_directories(validator)
    validate_text_content(validator)
    run_safe_skill_smoke_tests(validator)

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
