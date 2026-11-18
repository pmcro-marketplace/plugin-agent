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

## Standalone fleet release gate

Run from the Plugin Agent root on Python 3.12 with Git:

```sh
python -m venv /tmp/pmcro-check-venv
. /tmp/pmcro-check-venv/bin/activate
python -m pip install --only-binary=:all: --require-hashes -r requirements-ci.txt
python -B -m unittest discover -s tests -v
python -B skills/plugin/scripts/verify_fleet.py --fetch
```

The gate checks this candidate and twelve reviewed GitHub snapshots. It verifies exact repository origins, revision pins, manifest parity, portable skill layout, expected skill names, and Python syntax without running code from the checked packages. Use `--checkouts /absolute/fleet` for matching fresh local snapshots. A PASS is a static gate, not a native install, runtime check, model evaluation or permission to publish.

When promoting a package, validate its candidate separately, run its domain tests and host-specific acceptance checks, and update `skills/plugin/assets/fleet-lock.json` only after its reviewed revision is publicly fetchable. Keep prior pins as the rollback baseline. The Marketplace Agent pin remains on its published baseline until its standalone candidate is approved and available upstream.

For a separate native installation and skill inventory check, provide already reviewed package roots to `node tests/smoke_codex.mjs /absolute/agent-a /absolute/agent-b`. It requires Node 20+ and a Codex CLI exposing local `plugin/read` and `plugin/install` over the app server (tested with 0.130.0). It stages a temporary `CODEX_HOME` and fixture marketplace, installs only the supplied packages, and cleans up. It does not run a model, skill, or provider or test other hosts.
