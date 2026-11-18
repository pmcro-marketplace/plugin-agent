import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / "skills/plugin/scripts/validate_package.py"
SPEC = importlib.util.spec_from_file_location("validate_package", SCRIPT)
audit = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(audit)


class ValidatePackageTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        (self.root / ".codex-plugin").mkdir()
        self.skill = self.root / "skills/fixture"
        self.skill.mkdir(parents=True)
        (self.skill / "SKILL.md").write_text("---\nname: fixture\ndescription: Test packaging.\n---\n")
        self.canonical = {"$schema": audit.SCHEMA, "name": "fixture", "version": "1.2.3",
                          "author": {"name": "Fixture", "email": "example@example.org"},
                          "extensions": {"com.openai": {"interface": {"displayName": "Fixture"}}}}
        self.codex = {"name": "fixture", "version": "1.2.3", "skills": "./skills",
                      "author": {"email": "example@example.org", "name": "Fixture"},
                      "interface": {"displayName": "Fixture"}}

    def check(self, validator="/host/agentskills"):
        (self.root / "plugin.json").write_text(json.dumps(self.canonical))
        (self.root / ".codex-plugin/plugin.json").write_text(json.dumps(self.codex))
        with patch.object(audit, "check_skill", return_value=None):
            return audit.audit(self.root, validator)

    def test_matching_projection_ignores_json_key_order(self):
        result = self.check()
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["host_installation"], "NOT_TESTED")
        self.assertEqual(result["invocation"], "NOT_INVOKED")

    def test_rejects_drift(self):
        self.codex["version"] = "1.2.4"
        self.codex["interface"]["displayName"] = "Drift"
        result = self.check()
        self.assertEqual(result["status"], "FAIL")
        self.assertEqual(len(result["errors"]), 2)

    def test_rejects_missing_skill(self):
        (self.skill / "SKILL.md").unlink()
        self.assertEqual(self.check()["status"], "FAIL")

    def test_rejects_unavailable_skill_validator(self):
        self.assertIn("CLI is missing", "\n".join(self.check(None)["errors"]))

    def test_canonical_schema_does_not_allow_codex_paths(self):
        self.canonical["skills"] = "./skills"
        self.assertIn("unknown canonical fields: skills", "\n".join(self.check()["errors"]))

    def test_duplicate_keys_are_not_silently_accepted(self):
        path = self.root / "bad.json"
        path.write_text('{"name":"one","name":"two"}')
        with self.assertRaisesRegex(ValueError, "duplicate key"):
            audit.read_manifest(path)


if __name__ == "__main__":
    unittest.main()
