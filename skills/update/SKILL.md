---
name: update
description: Update an existing owned plugin through Plugin Creator while preserving its identity, release guard, and audience. USE FOR authorized changes to an existing plugin package. DO NOT USE FOR creating a missing plugin, marketplace catalog changes, or plugin-domain routing; use a create skill, Marketplace Agent, or plugin.
---
# update

## Purpose
Inspect an existing plugin, prepare the narrowest authorized change, invoke the real update provider, and verify the saved result.

## When to Use
Use when the target plugin already exists and the requested change preserves its domain identity.

## When Not to Use
Do not create missing plugins, change marketplace membership, or use this as a routing-only skill.

## Inputs
Owned plugin identity, current package/source, requested change, release/audience constraints, authorization, and expected state.

## Deliverables
A verified updated plugin package or `BLOCKED` / `NOT_INVOKED`.

## Workflow
1. Read the current owned plugin and preserve its identity.
2. Bound the requested change and release constraints.
3. Resolve Plugin Creator as the real update provider.
4. Invoke the update.
5. Read back and validate the saved package before reporting PASS.

## Validation
PASS requires provider evidence plus read-back validation of the updated plugin.

## Pitfalls
Do not overwrite unrelated changes or treat local preparation as proof of saved provider state.

## Resources
See `references/contract.md`, `assets/request.json`, and `scripts/validate.py`.
