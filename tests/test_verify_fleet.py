import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[1] / "skills/plugin/scripts"
sys.path.insert(0, str(SCRIPTS))

import verify_fleet as fleet


class VerifyFleetTests(unittest.TestCase):
    def test_inventory_includes_all_twelve_other_repos(self):
        self.assertEqual(len(fleet.load_lock()), 12)
        self.assertNotIn("plugin-agent", fleet.load_lock())

    def test_incomplete_or_unpinned_inventory_fails_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "lock.json"
            data = {"version": 1, "reviewed": fleet.load_lock()}
            data["reviewed"]["marketplace-agent"][0] = "main"
            path.write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError, "Invalid source pin"):
                fleet.load_lock(path)
            del data["reviewed"]["marketplace-agent"]
            path.write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError, "Invalid fleet inventory"):
                fleet.load_lock(path)

    def test_changed_and_unreviewed_checkouts_are_not_audited(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            repo = "marketplace-agent"
            sha = fleet.load_lock()[repo][0]
            for results, error in (
                ([str(root), fleet.origin(repo), "0" * 40], "HEAD differs"),
                ([str(root), "https://github.com/untrusted/marketplace-agent", sha], "Origin differs"),
                ([str(root), fleet.origin(repo), sha, "?? skills/surprise"], "local changes"),
            ):
                with patch.object(fleet, "git", side_effect=results):
                    with self.assertRaisesRegex(ValueError, error):
                        fleet.check_checkout(root, repo, sha)
