# Plugin Agent

Canonical plugin: `plugin`. Human handle: `@plugin-agent`.

Governed plugin discovery, creation, migration, and update routing through Plugin Creator.

The package follows the invocation contract in `INVOCATION.md`. Legacy packages are not retired by installing this canonical package.

## Check package alignment

With Python 3 and the `agentskills` CLI, run this from the Plugin Agent checkout:

```sh
python3 -B skills/plugin/scripts/validate_package.py /absolute/agent-a /absolute/agent-b
```

The check compares the canonical `plugin.json` to the shared fields in the
Codex projection, then checks each portable skill. It does not install hosts,
run providers, or enforce the proposed Skill Creator vNext policies.
