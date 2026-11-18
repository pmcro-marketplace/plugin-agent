---
name: create-template
description: Create or migrate the canonical template plugin only after discovery proves a gap. USE FOR creating or migrating the canonical template plugin package. DO NOT USE FOR individual reusable templates, other canonical plugins, generic domain plugins, or existing plugin updates; use Template Agent or the matching sibling skill.
---
# create-template

## Purpose
Create or migrate the canonical template plugin package while leaving template-domain content ownership to Template Agent.

## When to Use
Use only when discovery proves the canonical template plugin package is missing or requires migration.

## When Not to Use
Do not create an individual reusable template; use Template Agent. Do not create marketplace, pmcro, or generic domain plugins. Do not modify an existing package when `update` is sufficient.

## Inputs
Discovery evidence, existing package source if migrating, required template-plugin capabilities, and authorization.

## Deliverables
A validated canonical template plugin package or `BLOCKED` / `NOT_INVOKED`.

## Workflow
1. Prove a package gap or migration need.
2. Preserve canonical template plugin identity.
3. Resolve Plugin Creator as implementation authority.
4. Create or migrate the package without duplicating Template Agent's domain work.
5. Validate and read back the saved package.

## Validation
PASS requires real saved-package evidence plus validation.

## Pitfalls
A template plugin package is not an individual template artifact and is not marketplace membership.

## Resources
See `references/contract.md`, `assets/request.json`, and `scripts/validate.py`.
