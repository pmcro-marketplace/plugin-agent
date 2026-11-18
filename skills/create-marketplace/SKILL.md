---
name: create-marketplace
description: Create or migrate the canonical marketplace plugin only after discovery proves a gap. USE FOR creating or migrating the canonical marketplace plugin package. DO NOT USE FOR marketplace catalog membership, generic domain plugins, PMCR-O/template plugins, or existing plugin updates; use the owning sibling skill or Marketplace Agent.
---
# create-marketplace

## Purpose
Create or migrate the canonical marketplace plugin package while preserving Marketplace Agent ownership of catalogs and membership.

## When to Use
Use only when the canonical marketplace plugin package is missing or requires an authorized migration.

## When Not to Use
Do not create or edit marketplace catalogs; use Marketplace Agent. Do not create generic domain, pmcro, or template plugins; use the corresponding sibling creation skill. Do not update an existing owned package when `update` is sufficient.

## Inputs
Discovery evidence, existing marketplace-plugin source if migrating, target package identity, required capabilities, and authorization.

## Deliverables
A validated canonical marketplace plugin package or `BLOCKED` / `NOT_INVOKED`.

## Workflow
1. Prove a creation or migration gap exists.
2. Preserve the canonical marketplace plugin identity.
3. Resolve Plugin Creator as implementation authority.
4. Create or migrate the package without taking ownership of catalog state.
5. Validate and read back the saved package before PASS.

## Validation
PASS requires provider-backed saved-package evidence plus validation.

## Pitfalls
Plugin creation is not marketplace creation, membership, installation, or execution.

## Resources
See `references/contract.md`, `assets/request.json`, and `scripts/validate.py`.
