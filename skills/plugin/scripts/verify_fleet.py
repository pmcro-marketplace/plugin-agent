"""Verify Plugin Agent and the immutable, reviewed PMCR-O package fleet."""

import argparse
import json
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

from validate_package import audit, read_manifest

SELF = Path(__file__).resolve().parents[3]
LOCK = Path(__file__).resolve().parents[1] / "assets/fleet-lock.json"
ORG = "pmcro-marketplace"
SELF_SKILLS = ["create-domain", "create-marketplace", "create-pmcro", "create-template", "plugin", "update"]
REPOSITORIES = frozenset(
    f"{name}-agent" for name in ("checker", "docker", "github", "hook", "maker", "marketplace",
                                "orchestrator", "planner", "pmcro", "reflector", "skill", "template")
)


def require(condition, explanation):
    if not condition:
        raise ValueError(explanation)


def load_lock(path=LOCK):
    data = read_manifest(path)
    require(set(data) == {"version", "reviewed"} and type(data["version"]) is int
            and data["version"] == 1 and isinstance(data["reviewed"], dict)
            and data["reviewed"].keys() == REPOSITORIES, "Invalid fleet inventory")
    for repo, entry in data["reviewed"].items():
        require(isinstance(entry, list) and len(entry) == 3, f"Invalid lock entry for {repo}")
        sha, plugin, skills = entry
        require(isinstance(sha, str) and re.fullmatch("[a-f0-9]{40}", sha)
                and repo == f"{plugin}-agent", f"Invalid source pin for {repo}")
        require(isinstance(skills, list) and skills and all(isinstance(s, str) for s in skills)
                and skills == sorted(set(skills)), f"Invalid skill inventory for {repo}")
    return data["reviewed"]


def git(root, *args):
    env = {**os.environ, "GIT_TERMINAL_PROMPT": "0"}
    return subprocess.run(["git", "--no-replace-objects", "-C", str(root), *args],
                          check=True, capture_output=True, text=True, timeout=90, env=env).stdout.strip()


def origin(repo):
    return f"https://github.com/{ORG}/{repo}.git"


def fetch(root, repo, sha):
    root.mkdir()
    git(root, "init", "--quiet")
    git(root, "remote", "add", "origin", origin(repo))
    git(root, "-c", "protocol.file.allow=never", "fetch", "--quiet", "--depth=1", "--no-tags", "origin", sha)
    git(root, "checkout", "--quiet", "--detach", sha)


def check_checkout(root, repo, sha):
    require(root.is_dir() and not root.is_symlink(), "Checkout directory is missing or a symlink")
    require(Path(git(root, "rev-parse", "--show-toplevel")).resolve() == root.resolve(), "Not a repository root")
    require(git(root, "remote", "get-url", "origin") in {origin(repo), origin(repo)[:-4]}, "Origin differs from lock")
    require(git(root, "rev-parse", "HEAD") == sha, "HEAD differs from reviewed pin")
    # Include ignored files: an ignored SKILL.md or script must not enter the audited package.
    require(not git(root, "status", "--porcelain=v1", "--untracked-files=all", "--ignored=matching"),
            "Checkout has local changes or untracked files; use a fresh snapshot")


def audit_identity(root, name, skills, validator):
    report = audit(root, validator)
    if report["plugin"] != name or report["skills"] != skills:
        report["errors"].append("Plugin identity or skill inventory differs from lock")
        report["status"] = "FAIL"
    del report["root"]
    return report


def verify(directory, *, download=False):
    validator = shutil.which("agentskills")
    current = audit_identity(SELF, "plugin", SELF_SKILLS, validator)
    results = [{"repository": "plugin-agent", "scope": "current-source-tree", **current}]
    for repo, (sha, plugin, skills) in sorted(load_lock().items()):
        root = directory / repo
        result = {"repository": repo, "revision": sha, "scope": "reviewed-pin"}
        try:
            if download:
                fetch(root, repo, sha)
            check_checkout(root, repo, sha)
            result.update(audit_identity(root, plugin, skills, validator))
        except (OSError, ValueError, subprocess.SubprocessError) as exc:
            # Never expose remote stderr or local paths in a CI summary.
            reason = str(exc) if type(exc) is ValueError else type(exc).__name__
            result.update(status="FAIL", errors=[reason])
        results.append(result)
    passed = all(result["status"] == "PASS" for result in results)
    return {"status": "PASS" if passed else "FAIL", "packages": len(results),
            "skills_passed": sum(len(row["skills"]) for row in results if row["status"] == "PASS"),
            "scope": "STATIC_ONLY", "provider_invocation": "NOT_INVOKED", "results": results}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--checkouts", type=Path, help="Directory containing twelve exact clean snapshots")
    mode.add_argument("--fetch", action="store_true", help="Fetch public immutable pins to temporary storage")
    args = parser.parse_args()
    try:
        if args.fetch:
            with tempfile.TemporaryDirectory(prefix="pmcro-fleet-") as directory:
                report = verify(Path(directory), download=True)
        else:
            report = verify(args.checkouts.resolve(strict=True))
        print(json.dumps(report, indent=2))
        return 0 if report["status"] == "PASS" else 1
    except (OSError, ValueError, RecursionError):
        print(json.dumps({"status": "FAIL", "error": "Could not load fleet lock or checkout root"}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
