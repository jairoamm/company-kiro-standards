#!/usr/bin/env python3
"""Install versioned Kiro Steering and Skills from this local repository."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
import tempfile
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Set


class SyncError(RuntimeError):
    """Raised when the sync cannot proceed safely."""


@dataclass(frozen=True)
class Asset:
    asset_id: str
    source: PurePosixPath
    target: PurePosixPath
    kind: str


@dataclass(frozen=True)
class PlannedChange:
    asset: Asset
    source_path: Path
    target_path: Path
    action: str
    source_hash: str
    target_hash: Optional[str]


REPOSITORY_ROOT = Path(__file__).resolve().parent.parent
STATE_DIRECTORY = ".standards-hub"
MANIFEST_NAME = "manifest.json"


def load_json(path: Path) -> Mapping[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as error:
        raise SyncError(f"Required file does not exist: {path}") from error
    except json.JSONDecodeError as error:
        raise SyncError(f"Invalid JSON in {path}: {error}") from error

    if not isinstance(value, dict):
        raise SyncError(f"Expected a JSON object in {path}")
    return value


def write_json_atomic(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=str(path.parent)
    )
    temporary_path = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            json.dump(value, stream, indent=2, sort_keys=True)
            stream.write("\n")
        os.replace(temporary_path, path)
    finally:
        temporary_path.unlink(missing_ok=True)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def safe_relative_path(raw_value: Any, label: str) -> PurePosixPath:
    if not isinstance(raw_value, str) or not raw_value.strip():
        raise SyncError(f"{label} must be a non-empty string")
    if "\\" in raw_value:
        raise SyncError(f"{label} must use forward slashes: {raw_value}")

    path = PurePosixPath(raw_value)
    if path.is_absolute() or path == PurePosixPath(".") or ".." in path.parts:
        raise SyncError(f"Unsafe {label}: {raw_value}")
    return path


def filesystem_path(root: Path, relative: PurePosixPath) -> Path:
    return root.joinpath(*relative.parts)


def is_within(candidate: Path, parent: Path) -> bool:
    try:
        candidate.relative_to(parent)
        return True
    except ValueError:
        return False


def reject_symlink_components(path: Path) -> None:
    current = Path(path.anchor)
    for part in path.parts[1:]:
        current = current / part
        if current.exists() and current.is_symlink():
            raise SyncError(f"Symlink path component is not allowed: {current}")


def resolve_kiro_home(raw_value: str) -> Path:
    expanded = Path(raw_value).expanduser()
    if not expanded.is_absolute():
        raise SyncError("--kiro-home must be an absolute path")

    resolved = expanded.resolve(strict=False)
    reject_symlink_components(resolved)
    home = Path.home().resolve()
    repository = REPOSITORY_ROOT.resolve()

    if resolved == Path(resolved.anchor) or resolved == home:
        raise SyncError("Refusing to use the filesystem root or user home as KIRO_HOME")
    if resolved == repository or is_within(resolved, repository):
        raise SyncError("KIRO_HOME cannot be this standards repository or a child of it")
    if not resolved.parent.exists():
        raise SyncError(
            f"Parent directory must already exist: {resolved.parent}. "
            "Create an isolated parent explicitly before syncing."
        )
    return resolved


def parse_catalog() -> tuple[str, Dict[str, Asset]]:
    catalog = load_json(REPOSITORY_ROOT / "catalog.json")
    version = catalog.get("version")
    raw_assets = catalog.get("assets")
    if not isinstance(version, str) or not version:
        raise SyncError("catalog.json is missing version")
    if not isinstance(raw_assets, list):
        raise SyncError("catalog.json assets must be an array")

    assets: Dict[str, Asset] = {}
    for raw_asset in raw_assets:
        if not isinstance(raw_asset, dict):
            raise SyncError("Every catalog asset must be an object")
        asset_id = raw_asset.get("id")
        kind = raw_asset.get("kind")
        if not isinstance(asset_id, str) or not asset_id:
            raise SyncError("Every catalog asset needs a non-empty id")
        if asset_id in assets:
            raise SyncError(f"Duplicate catalog asset id: {asset_id}")
        if kind not in {"steering", "skill"}:
            raise SyncError(f"Unsupported kind for {asset_id}: {kind}")
        source = safe_relative_path(raw_asset.get("source"), f"source for {asset_id}")
        target = safe_relative_path(raw_asset.get("target"), f"target for {asset_id}")
        expected_prefix = "steering" if kind == "steering" else "skills"
        if not target.parts or target.parts[0] != expected_prefix:
            raise SyncError(
                f"Target for {asset_id} must be below {expected_prefix}/: {target}"
            )
        assets[asset_id] = Asset(asset_id, source, target, kind)
    return version, assets


def read_bundle(name: str) -> Mapping[str, Any]:
    if not name or any(character not in "abcdefghijklmnopqrstuvwxyz0123456789-_" for character in name):
        raise SyncError(f"Invalid bundle name: {name}")
    return load_json(REPOSITORY_ROOT / "bundles" / f"{name}.json")


def resolve_bundle_assets(
    name: str,
    catalog_assets: Mapping[str, Asset],
    visiting: Optional[Set[str]] = None,
    resolved_bundles: Optional[Set[str]] = None,
) -> List[Asset]:
    active = set() if visiting is None else visiting
    completed = set() if resolved_bundles is None else resolved_bundles
    if name in active:
        raise SyncError(f"Bundle inheritance cycle detected at: {name}")
    if name in completed:
        return []

    active.add(name)
    bundle = read_bundle(name)
    declared_name = bundle.get("name")
    if declared_name != name:
        raise SyncError(f"Bundle filename/name mismatch: {name} != {declared_name}")

    extends = bundle.get("extends", [])
    asset_ids = bundle.get("assets", [])
    if not isinstance(extends, list) or not all(isinstance(item, str) for item in extends):
        raise SyncError(f"Bundle {name} has invalid extends")
    if not isinstance(asset_ids, list) or not all(isinstance(item, str) for item in asset_ids):
        raise SyncError(f"Bundle {name} has invalid assets")

    ordered: List[Asset] = []
    for parent in extends:
        ordered.extend(resolve_bundle_assets(parent, catalog_assets, active, completed))

    for asset_id in asset_ids:
        asset = catalog_assets.get(asset_id)
        if asset is None:
            raise SyncError(f"Bundle {name} references unknown asset: {asset_id}")
        ordered.append(asset)

    active.remove(name)
    completed.add(name)

    unique: Dict[str, Asset] = {}
    for asset in ordered:
        unique.setdefault(asset.asset_id, asset)
    return list(unique.values())


def read_manifest(kiro_home: Path) -> Optional[Mapping[str, Any]]:
    path = kiro_home / STATE_DIRECTORY / MANIFEST_NAME
    if not path.exists():
        return None
    if path.is_symlink():
        raise SyncError(f"Managed manifest cannot be a symlink: {path}")
    return load_json(path)


def manifest_targets(manifest: Optional[Mapping[str, Any]]) -> Dict[str, Mapping[str, Any]]:
    if manifest is None:
        return {}
    raw_files = manifest.get("files")
    if not isinstance(raw_files, list):
        raise SyncError("Installed manifest has invalid files")
    result: Dict[str, Mapping[str, Any]] = {}
    for entry in raw_files:
        if not isinstance(entry, dict):
            raise SyncError("Installed manifest has an invalid file entry")
        target = safe_relative_path(entry.get("target"), "installed target").as_posix()
        result[target] = entry
    return result


def build_plan(
    assets: Sequence[Asset], kiro_home: Path, manifest: Optional[Mapping[str, Any]]
) -> List[PlannedChange]:
    previous_targets = manifest_targets(manifest)
    changes: List[PlannedChange] = []

    for asset in assets:
        source_path = filesystem_path(REPOSITORY_ROOT, asset.source)
        if not source_path.is_file() or source_path.is_symlink():
            raise SyncError(f"Asset source must be a regular file: {asset.source}")

        target_path = filesystem_path(kiro_home, asset.target)
        if target_path.exists() and target_path.is_symlink():
            raise SyncError(f"Refusing to manage symlink target: {target_path}")
        reject_symlink_components(target_path.parent)

        source_hash = sha256(source_path)
        target_hash = sha256(target_path) if target_path.is_file() else None
        target_key = asset.target.as_posix()

        previous_entry = previous_targets.get(target_key)
        if target_path.exists() and previous_entry is None:
            action = "CONFLICT"
        elif target_hash is None and previous_entry is not None:
            action = "LOCAL_MISSING"
        elif (
            previous_entry is not None
            and target_hash != previous_entry.get("sha256")
        ):
            action = "LOCAL_MODIFIED"
        elif target_hash is None:
            action = "ADD"
        elif target_hash == source_hash:
            action = "UNCHANGED"
        else:
            action = "UPDATE"

        changes.append(
            PlannedChange(asset, source_path, target_path, action, source_hash, target_hash)
        )
    return changes


def print_plan(bundle: str, version: str, kiro_home: Path, plan: Iterable[PlannedChange]) -> None:
    print(f"Bundle: {bundle}")
    print(f"Version: {version}")
    print(f"KIRO_HOME: {kiro_home}")
    for change in plan:
        print(f"{change.action:9} {change.asset.target.as_posix()}")


def copy_atomic(source: Path, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{target.name}.", suffix=".tmp", dir=str(target.parent)
    )
    os.close(descriptor)
    temporary_path = Path(temporary_name)
    try:
        shutil.copyfile(source, temporary_path)
        shutil.copymode(source, temporary_path)
        os.replace(temporary_path, target)
    finally:
        temporary_path.unlink(missing_ok=True)


def backup_id() -> str:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"{timestamp}-{uuid.uuid4().hex[:8]}"


def restore_backup(kiro_home: Path, backup_directory: Path, verify_current: bool) -> None:
    metadata = load_json(backup_directory / "metadata.json")
    raw_operations = metadata.get("operations")
    if not isinstance(raw_operations, list):
        raise SyncError(f"Backup metadata has invalid operations: {backup_directory}")

    if verify_current:
        for operation in raw_operations:
            if not isinstance(operation, dict):
                raise SyncError("Backup operation must be an object")
            relative = safe_relative_path(operation.get("target"), "backup target")
            target = filesystem_path(kiro_home, relative)
            expected_hash = operation.get("afterHash")
            if not target.is_file() or sha256(target) != expected_hash:
                raise SyncError(
                    f"Refusing rollback because the installed file changed: {relative}"
                )

    for operation in reversed(raw_operations):
        if not isinstance(operation, dict):
            raise SyncError("Backup operation must be an object")
        relative = safe_relative_path(operation.get("target"), "backup target")
        target = filesystem_path(kiro_home, relative)
        before_existed = operation.get("beforeExisted") is True
        if before_existed:
            backup_file = filesystem_path(backup_directory / "files", relative)
            if not backup_file.is_file():
                raise SyncError(f"Backup file is missing: {backup_file}")
            copy_atomic(backup_file, target)
        else:
            if target.exists():
                if not target.is_file() or target.is_symlink():
                    raise SyncError(f"Refusing to remove non-regular target: {target}")
                target.unlink()

    manifest_path = kiro_home / STATE_DIRECTORY / MANIFEST_NAME
    previous_manifest = backup_directory / "previous-manifest.json"
    if previous_manifest.exists():
        copy_atomic(previous_manifest, manifest_path)
    else:
        manifest_path.unlink(missing_ok=True)


def apply_plan(
    bundle: str,
    version: str,
    kiro_home: Path,
    plan: Sequence[PlannedChange],
    previous_manifest: Optional[Mapping[str, Any]],
) -> None:
    blockers = [
        change
        for change in plan
        if change.action in {"CONFLICT", "LOCAL_MODIFIED", "LOCAL_MISSING"}
    ]
    if blockers:
        details = ", ".join(
            f"{change.action}:{change.asset.target.as_posix()}"
            for change in blockers
        )
        raise SyncError(
            "Refusing to overwrite unmanaged or locally changed files: " + details
        )

    if previous_manifest is not None and previous_manifest.get("bundle") != bundle:
        raise SyncError(
            "This KIRO_HOME is already managed with bundle "
            f"{previous_manifest.get('bundle')}. Use a separate KIRO_HOME or rollback first."
        )

    if previous_manifest is not None:
        previous_target_names = set(manifest_targets(previous_manifest))
        selected_target_names = {
            change.asset.target.as_posix() for change in plan
        }
        stale_targets = sorted(previous_target_names - selected_target_names)
        if stale_targets:
            raise SyncError(
                "The new release omits previously managed files. "
                "Explicit migration is required before applying: "
                + ", ".join(stale_targets)
            )

    changed = [change for change in plan if change.action in {"ADD", "UPDATE"}]
    if not changed:
        print("No changes to apply.")
        return

    state_directory = kiro_home / STATE_DIRECTORY
    backups_directory = state_directory / "backups"
    current_backup_id = backup_id()
    backup_directory = backups_directory / current_backup_id
    backup_directory.mkdir(parents=True, exist_ok=False)

    manifest_path = state_directory / MANIFEST_NAME
    if manifest_path.exists():
        copy_atomic(manifest_path, backup_directory / "previous-manifest.json")

    operations: List[Dict[str, Any]] = []
    for change in changed:
        relative = change.asset.target
        if change.target_path.exists():
            copy_atomic(change.target_path, filesystem_path(backup_directory / "files", relative))
        operations.append(
            {
                "target": relative.as_posix(),
                "beforeExisted": change.target_path.exists(),
                "beforeHash": change.target_hash,
                "afterHash": change.source_hash,
            }
        )

    metadata: Dict[str, Any] = {
        "backupId": current_backup_id,
        "createdAt": datetime.now(timezone.utc).isoformat(),
        "bundle": bundle,
        "version": version,
        "operations": operations,
    }
    write_json_atomic(backup_directory / "metadata.json", metadata)

    try:
        for change in changed:
            copy_atomic(change.source_path, change.target_path)

        files = [
            {
                "assetId": change.asset.asset_id,
                "kind": change.asset.kind,
                "source": change.asset.source.as_posix(),
                "target": change.asset.target.as_posix(),
                "sha256": change.source_hash,
            }
            for change in plan
        ]
        manifest: Dict[str, Any] = {
            "schemaVersion": "1.0",
            "repository": "bam-kiro-standards",
            "bundle": bundle,
            "version": version,
            "installedAt": datetime.now(timezone.utc).isoformat(),
            "backupId": current_backup_id,
            "files": files,
        }
        write_json_atomic(manifest_path, manifest)
    except Exception:
        restore_backup(kiro_home, backup_directory, verify_current=False)
        raise

    print(f"Applied bundle {bundle} version {version}.")
    print(f"Backup ID: {current_backup_id}")


def select_backup(kiro_home: Path, requested: str) -> Path:
    backups_directory = kiro_home / STATE_DIRECTORY / "backups"
    if not backups_directory.is_dir():
        raise SyncError("No backups are available")
    candidates = sorted(path for path in backups_directory.iterdir() if path.is_dir())
    if not candidates:
        raise SyncError("No backups are available")
    if requested == "latest":
        return candidates[-1]
    if "/" in requested or "\\" in requested or ".." in requested:
        raise SyncError(f"Invalid backup id: {requested}")
    selected = backups_directory / requested
    if not selected.is_dir():
        raise SyncError(f"Backup does not exist: {requested}")
    return selected


def parse_arguments(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Synchronize approved Kiro Steering and Skills from a local checkout."
    )
    parser.add_argument("--bundle", help="Bundle name from bundles/<name>.json")
    parser.add_argument(
        "--kiro-home",
        required=True,
        help="Explicit absolute KIRO_HOME destination. The user home itself is refused.",
    )
    action = parser.add_mutually_exclusive_group()
    action.add_argument("--dry-run", action="store_true", help="Show changes without writing")
    action.add_argument("--apply", action="store_true", help="Apply the planned changes")
    action.add_argument(
        "--verify",
        action="store_true",
        help="Fail unless the requested bundle and every managed file match",
    )
    action.add_argument(
        "--rollback",
        metavar="BACKUP_ID",
        help="Restore a backup id, or use 'latest'",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str]) -> int:
    try:
        arguments = parse_arguments(argv)
        kiro_home = resolve_kiro_home(arguments.kiro_home)

        if arguments.rollback:
            backup_directory = select_backup(kiro_home, arguments.rollback)
            restore_backup(kiro_home, backup_directory, verify_current=True)
            print(f"Rolled back backup: {backup_directory.name}")
            return 0

        if not arguments.bundle:
            raise SyncError("--bundle is required for dry-run and apply")

        version, catalog_assets = parse_catalog()
        assets = resolve_bundle_assets(arguments.bundle, catalog_assets)
        bundle = read_bundle(arguments.bundle)
        if bundle.get("version") != version:
            raise SyncError(
                f"Bundle/catalog version mismatch: {bundle.get('version')} != {version}"
            )

        manifest = read_manifest(kiro_home)
        plan = build_plan(assets, kiro_home, manifest)
        print_plan(arguments.bundle, version, kiro_home, plan)

        if arguments.verify:
            if manifest is None:
                raise SyncError("No managed installation manifest exists")
            if manifest.get("bundle") != arguments.bundle:
                raise SyncError(
                    f"Installed bundle is {manifest.get('bundle')}, not {arguments.bundle}"
                )
            if manifest.get("version") != version:
                raise SyncError(
                    f"Installed version is {manifest.get('version')}, not {version}"
                )
            expected_targets = {
                change.asset.target.as_posix() for change in plan
            }
            installed_targets = set(manifest_targets(manifest))
            if installed_targets != expected_targets:
                missing = sorted(expected_targets - installed_targets)
                extra = sorted(installed_targets - expected_targets)
                raise SyncError(
                    "Installed manifest does not match the requested bundle. "
                    f"Missing: {missing or 'none'}; extra: {extra or 'none'}"
                )
            mismatches = [change for change in plan if change.action != "UNCHANGED"]
            if mismatches:
                details = ", ".join(
                    f"{change.action}:{change.asset.target.as_posix()}"
                    for change in mismatches
                )
                raise SyncError("Installation verification failed: " + details)
            print(f"Verified bundle {arguments.bundle} version {version}.")
            return 0

        if arguments.apply:
            apply_plan(arguments.bundle, version, kiro_home, plan, manifest)
        else:
            print("Dry-run only. Use --apply to write these changes.")
        return 0
    except SyncError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2
    except OSError as error:
        print(f"ERROR: filesystem operation failed: {error}", file=sys.stderr)
        return 3


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
