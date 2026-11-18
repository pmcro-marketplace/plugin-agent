---
name: plugin
description: Act as the plugin-domain router and enforce discover-before-create. USE FOR resolving plugin-level requests to reuse, create, migrate, or update capabilities. DO NOT USE FOR performing the selected create/update operation itself; use create-domain, create-marketplace, create-pmcro, create-template, or update.
---
# plugin

## Purpose
Resolve plugin-level capability needs and reuse existing validated plugins before creation.

## When to Use
Use when a plugin request must first be classified and routed to the narrowest existing capability.

## When Not to Use
Do not perform creation or update work after routing; invoke the selected sibling skill.

## Inputs
A bounded plugin request, current plugin inventory/discovery evidence, authorization, and desired outcome.

## Deliverables
A concrete resolved plugin function or `BLOCKED` / `NOT_INVOKED`.

## Workflow
1. Inspect validated plugin inventory and discovery evidence.
2. Reuse an existing capability when it satisfies the request.
3. If a gap remains, select the narrowest creation or update skill.
4. Emit the exact target function identity.
5. Invoke the actual selected capability rather than simulating it.

## Validation
PASS requires target capability evidence, not routing output alone.

## Pitfalls
Discovery is not authorization. Emission is not invocation. Avoid duplicate plugins and agents.

## Resources
See `references/contract.md`, `assets/request.json`, and `scripts/validate.py`.
