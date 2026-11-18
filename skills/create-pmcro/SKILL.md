---
name: create-pmcro
description: Create or migrate the canonical pmcro plugin only after discovery proves a gap. USE FOR creating or migrating the canonical PMCR-O protocol plugin package. DO NOT USE FOR role-agent execution, other canonical plugins, generic domain plugins, or existing plugin updates; use the owning agent or sibling skill.
---
# create-pmcro

## Purpose
Create or migrate the canonical PMCR-O protocol plugin without prematurely retiring validated legacy PMCR-O capability.

## When to Use
Use when discovery proves the canonical PMCR-O package is missing or an authorized migration is required.

## When Not to Use
Do not run a PMCR-O cycle here. Do not create marketplace/template/domain plugins. Do not update an existing package when `update` is sufficient.

## Inputs
Discovery evidence, current PMCR-O package/source, required protocol capabilities, migration constraints, and authorization.

## Deliverables
A validated canonical PMCR-O plugin package or `BLOCKED` / `NOT_INVOKED`.

## Workflow
1. Establish the gap or migration requirement.
2. Preserve legacy PMCR-O until replacement verification succeeds.
3. Resolve Plugin Creator as implementation authority.
4. Create or migrate the canonical package with stable identity.
5. Validate the saved package and record replacement evidence.

## Validation
PASS requires a real saved package and proof the replacement is valid; declaring a migration is insufficient.

## Pitfalls
Never retire legacy PMCR-O before replacement proof. Packaging is not runtime execution.

## Resources
See `references/contract.md`, `assets/request.json`, and `scripts/validate.py`.
