#!/usr/bin/env python3
"""Unit tests for safe Skill directory distribution."""

from __future__ import annotations

import contextlib
import io
import tempfile
import unittest
from pathlib import Path, PurePosixPath
from unittest import mock

from tools import sync


class SkillPackagingTests(unittest.TestCase):
    def create_skill(self, root: Path, category: str, name: str) -> sync.Asset:
        skill_directory = root / "skills" / category / name
        (skill_directory / "examples").mkdir(parents=True)
        (skill_directory / "templates").mkdir()
        (skill_directory / "SKILL.md").write_text(
            f"---\nname: {name}\ndescription: synthetic test skill\n---\n",
            encoding="utf-8",
        )
        (skill_directory / "examples" / "example.json").write_text(
            '{"classification":"synthetic"}\n', encoding="utf-8"
        )
        (skill_directory / "templates" / "output.md").write_text(
            "# {{TITLE}}\n", encoding="utf-8"
        )
        return sync.Asset(
            f"skill-{name}",
            PurePosixPath(f"skills/{category}/{name}/SKILL.md"),
            PurePosixPath(f"skills/{name}/SKILL.md"),
            "skill",
        )

    def test_expands_complete_skill_directory(self) -> None:
        with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parent) as temporary:
            root = Path(temporary)
            asset = self.create_skill(root, "qa", "sample")
            with mock.patch.object(sync, "REPOSITORY_ROOT", root):
                expanded = sync.expand_assets([asset])

            self.assertEqual(
                [item.target.as_posix() for item in expanded],
                [
                    "skills/sample/SKILL.md",
                    "skills/sample/examples/example.json",
                    "skills/sample/templates/output.md",
                ],
            )
            self.assertTrue(all(item.asset_id == "skill-sample" for item in expanded))

    def test_rejects_symlink_inside_skill(self) -> None:
        with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parent) as temporary:
            root = Path(temporary)
            asset = self.create_skill(root, "qa", "sample")
            outside = root / "outside.txt"
            outside.write_text("outside\n", encoding="utf-8")
            link = root / "skills" / "qa" / "sample" / "examples" / "linked.txt"
            try:
                link.symlink_to(outside)
            except OSError as error:
                self.skipTest(f"symlinks unavailable: {error}")

            with mock.patch.object(sync, "REPOSITORY_ROOT", root):
                with self.assertRaisesRegex(sync.SyncError, "Symlinks are not allowed"):
                    sync.expand_assets([asset])

    def test_rejects_expanded_target_collision(self) -> None:
        with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parent) as temporary:
            root = Path(temporary)
            first = self.create_skill(root, "qa", "first")
            second = self.create_skill(root, "qa", "second")
            second = sync.Asset(
                second.asset_id,
                second.source,
                first.target,
                second.kind,
            )

            with mock.patch.object(sync, "REPOSITORY_ROOT", root):
                with self.assertRaisesRegex(sync.SyncError, "Target collision"):
                    sync.expand_assets([first, second])

    def test_adds_support_files_to_legacy_single_file_manifest(self) -> None:
        with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parent) as repository_temporary, tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parent) as consumer_temporary:
            root = Path(repository_temporary)
            kiro_home = Path(consumer_temporary) / ".kiro"
            kiro_home.mkdir()
            asset = self.create_skill(root, "qa", "sample")
            installed_skill = kiro_home / "skills" / "sample" / "SKILL.md"
            installed_skill.parent.mkdir(parents=True)
            installed_skill.write_text(
                (root / "skills" / "qa" / "sample" / "SKILL.md").read_text(
                    encoding="utf-8"
                ),
                encoding="utf-8",
            )
            manifest = {
                "files": [
                    {
                        "target": "skills/sample/SKILL.md",
                        "sha256": sync.sha256(installed_skill),
                    }
                ]
            }

            with mock.patch.object(sync, "REPOSITORY_ROOT", root):
                expanded = sync.expand_assets([asset])
                plan = sync.build_plan(expanded, kiro_home, manifest)

            actions = {change.asset.target.as_posix(): change.action for change in plan}
            self.assertEqual(actions["skills/sample/SKILL.md"], "UNCHANGED")
            self.assertEqual(actions["skills/sample/examples/example.json"], "ADD")
            self.assertEqual(actions["skills/sample/templates/output.md"], "ADD")

    def test_apply_manifest_and_rollback_cover_support_files(self) -> None:
        with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parent) as repository_temporary, tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parent) as consumer_temporary:
            root = Path(repository_temporary)
            kiro_home = Path(consumer_temporary) / ".kiro"
            kiro_home.mkdir()
            asset = self.create_skill(root, "qa", "sample")

            with mock.patch.object(sync, "REPOSITORY_ROOT", root):
                expanded = sync.expand_assets([asset])
                plan = sync.build_plan(expanded, kiro_home, None)
                with contextlib.redirect_stdout(io.StringIO()):
                    sync.apply_plan("qa", "0.2.4", kiro_home, plan, None)
                manifest = sync.read_manifest(kiro_home)
                self.assertIsNotNone(manifest)
                assert manifest is not None
                targets = {
                    entry["target"]
                    for entry in manifest["files"]
                    if isinstance(entry, dict)
                }
                self.assertEqual(
                    targets,
                    {
                        "skills/sample/SKILL.md",
                        "skills/sample/examples/example.json",
                        "skills/sample/templates/output.md",
                    },
                )
                backup_id = manifest["backupId"]
                backup_directory = (
                    kiro_home / sync.STATE_DIRECTORY / "backups" / str(backup_id)
                )
                sync.restore_backup(kiro_home, backup_directory, verify_current=True)

            self.assertFalse((kiro_home / "skills" / "sample" / "SKILL.md").exists())
            self.assertFalse(
                (kiro_home / "skills" / "sample" / "examples" / "example.json").exists()
            )
            self.assertFalse(
                (kiro_home / sync.STATE_DIRECTORY / sync.MANIFEST_NAME).exists()
            )

    def test_rejects_target_symlink_component(self) -> None:
        with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parent) as repository_temporary, tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parent) as consumer_temporary, tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parent) as outside_temporary:
            root = Path(repository_temporary)
            kiro_home = Path(consumer_temporary) / ".kiro"
            kiro_home.mkdir()
            try:
                (kiro_home / "skills").symlink_to(Path(outside_temporary))
            except OSError as error:
                self.skipTest(f"symlinks unavailable: {error}")
            asset = self.create_skill(root, "qa", "sample")

            with mock.patch.object(sync, "REPOSITORY_ROOT", root):
                expanded = sync.expand_assets([asset])
                with self.assertRaisesRegex(sync.SyncError, "Symlink path component"):
                    sync.build_plan(expanded, kiro_home, None)

    def test_catalog_skills_expand_their_support_files(self) -> None:
        _, catalog_assets = sync.parse_catalog()
        skill_assets = [
            asset for asset in catalog_assets.values() if asset.kind == "skill"
        ]
        expanded = sync.expand_assets(skill_assets)
        targets_by_asset: dict[str, set[str]] = {}
        for asset_file in expanded:
            targets_by_asset.setdefault(asset_file.asset_id, set()).add(
                asset_file.target.as_posix()
            )

        self.assertEqual(set(targets_by_asset), {asset.asset_id for asset in skill_assets})
        self.assertTrue(all(len(targets) > 1 for targets in targets_by_asset.values()))
        self.assertIn(
            "skills/generate-selenium-tests/schemas/ui-selectors.schema.json",
            targets_by_asset["skill-generate-selenium-tests"],
        )
        self.assertIn(
            "skills/generate-postman-collection/templates/local.postman_environment.json",
            targets_by_asset["skill-generate-postman-collection"],
        )

    def test_rejects_duplicate_manifest_targets(self) -> None:
        manifest = {
            "files": [
                {"target": "skills/sample/SKILL.md"},
                {"target": "skills/SAMPLE/skill.md"},
            ]
        }
        with self.assertRaisesRegex(sync.SyncError, "duplicate target"):
            sync.manifest_targets(manifest)

    def test_rejects_relative_path_traversal(self) -> None:
        with self.assertRaisesRegex(sync.SyncError, "Unsafe test path"):
            sync.safe_relative_path("skills/../outside.md", "test path")


if __name__ == "__main__":
    unittest.main()
