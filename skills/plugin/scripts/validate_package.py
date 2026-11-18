"""Check PMCR-O plugin packaging and Codex projection parity without installing it."""

import argparse
import json
import re
import shutil
import subprocess
from pathlib import Path

SCHEMA = "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"
NAME = re.compile(r"(?!.*(?:--|\.\.))[a-z0-9](?:[a-z0-9.-]*[a-z0-9])?\Z")
TEXT = {"version", "description", "homepage", "repository", "license"}
ROOT_FIELDS = {"$schema", "name", "author", "keywords", "extensions"} | TEXT
SHARED = ("name", "version", "description", "author", "homepage", "repository", "license", "keywords")


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate key: {key}")
        result[key] = value
    return result


def read_manifest(path):
    if path.is_symlink() or not path.is_file():
        raise ValueError(f"expected a regular file: {path.name}")
    with path.open("rb") as stream:
        raw = stream.read(262145)
    if len(raw) > 262144:
        raise ValueError("manifest exceeds 256 KiB")
    def invalid_constant(value):
        raise ValueError(f"invalid JSON constant: {value}")
    data = json.loads(raw, object_pairs_hook=unique_object, parse_constant=invalid_constant)
    if not isinstance(data, dict):
        raise ValueError("manifest must contain a JSON object")
    return data


def canonical_errors(manifest):
    errors = []
    if manifest.get("$schema") != SCHEMA:
        errors.append("plugin.json: expected the Agent Plugins 1.0 schema identifier")
    name = manifest.get("name")
    if not isinstance(name, str) or not 1 <= len(name) <= 64 or not NAME.fullmatch(name):
        errors.append("plugin.json: invalid plugin name")
    unknown = sorted(set(manifest) - ROOT_FIELDS)
    if unknown:
        errors.append("plugin.json: unknown canonical fields: " + ", ".join(unknown))
    for field in sorted(TEXT & manifest.keys()):
        if not isinstance(manifest[field], str):
            errors.append(f"plugin.json: {field} must be a string")
    if "keywords" in manifest and (not isinstance(manifest["keywords"], list) or
            not all(isinstance(value, str) for value in manifest["keywords"])):
        errors.append("plugin.json: keywords must be a list of strings")
    if "author" in manifest:
        author = manifest["author"]
        if (not isinstance(author, dict) or set(author) - {"name", "email", "url"} or
                not all(isinstance(value, str) for value in author.values())):
            errors.append("plugin.json: invalid author object")
    extensions = manifest.get("extensions", {})
    if not isinstance(extensions, dict) or not all(isinstance(value, dict) for value in extensions.values()):
        errors.append("plugin.json: extensions must map names to objects")
    return errors


def projection_errors(canonical, codex):
    errors = []
    for field in SHARED:
        if (field in canonical) != (field in codex) or canonical.get(field) != codex.get(field):
            errors.append(f".codex-plugin/plugin.json: {field} differs from plugin.json")
    if codex.get("skills") != "./skills":
        errors.append(".codex-plugin/plugin.json: expected the PMCR-O ./skills projection")
    interface = canonical.get("extensions", {}).get("com.openai", {})
    if ("interface" in interface) != ("interface" in codex) or interface.get("interface") != codex.get("interface"):
        errors.append(".codex-plugin/plugin.json: interface differs from plugin.json")
    return errors


def check_skill(skill, executable):
    try:
        process = subprocess.run([executable, "validate", str(skill)], capture_output=True, text=True,
                                 timeout=30, check=False)
    except (OSError, subprocess.SubprocessError):
        return f"skills/{skill.name}: Agent Skills validator failed to run"
    if process.returncode:
        return f"skills/{skill.name}: Agent Skills validation failed"
    return None


def audit(root, skills_validator):
    errors, names = [], []
    canonical, codex = None, None
    try:
        canonical = read_manifest(root / "plugin.json")
        errors.extend(canonical_errors(canonical))
    except (ValueError, OSError, RecursionError) as exc:
        errors.append(f"plugin.json: {exc}")
    try:
        host = root / ".codex-plugin"
        if host.is_symlink() or not host.is_dir():
            raise ValueError("expected a real .codex-plugin directory")
        codex = read_manifest(host / "plugin.json")
    except (ValueError, OSError, RecursionError) as exc:
        errors.append(f".codex-plugin/plugin.json: {exc}")
    if canonical is not None and codex is not None and not canonical_errors(canonical):
        errors.extend(projection_errors(canonical, codex))
    skills = root / "skills"
    if skills.is_symlink() or not skills.is_dir():
        errors.append("expected a real skills directory")
    else:
        for skill in sorted(skills.iterdir()):
            if skill.name.startswith(".") or not (skill.is_dir() or skill.is_symlink()):
                continue
            names.append(skill.name)
            entry = skill / "SKILL.md"
            if skill.is_symlink() or entry.is_symlink() or not entry.is_file():
                errors.append(f"skills/{skill.name}: expected a real skill directory with SKILL.md")
            elif skills_validator is not None:
                issue = check_skill(skill, skills_validator)
                if issue:
                    errors.append(issue)
        if not names:
            errors.append("no skill entries were found")
    if skills_validator is None:
        errors.append("agentskills CLI is missing; skill validation was not run")
    return {"root": str(root), "plugin": canonical.get("name") if canonical else None, "skills": names,
            "status": "PASS" if not errors else "FAIL", "errors": errors,
            "host_installation": "NOT_TESTED", "model_behavior": "NOT_TESTED", "invocation": "NOT_INVOKED"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("roots", type=Path, nargs="+", help="Local PMCR-O plugin checkout roots")
    args = parser.parse_args()
    executable = shutil.which("agentskills")
    results = [audit(root.resolve(), executable) for root in args.roots]
    passed = all(row["status"] == "PASS" for row in results)
    print(json.dumps({"status": "PASS" if passed else "FAIL", "results": results}, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
