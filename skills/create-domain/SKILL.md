---
name: create-domain
description: Create the narrowest missing domain plugin after discovery proves no validated plugin satisfies the need. USE FOR a new domain plugin after discover-before-create proves a genuine capability gap. DO NOT USE FOR marketplace, PMCR-O, or template canonical plugins, existing plugin updates, or plugin routing; use the matching sibling skill.
---
# create-domain

## Purpose
Create one narrowly named domain plugin only after reuse has been ruled out.

## When to Use
Use after discovery proves no existing validated plugin satisfies the requested domain capability.

## When Not to Use
Do not create the canonical marketplace, pmcro, or template plugins; use their dedicated creation skills. Do not modify an existing plugin; use `update`. Do not use this skill merely to route a plugin request; use `plugin`.

## Inputs
A bounded capability gap, proposed domain noun, intended audience, required skills, authorization context, and discovery evidence.

## Deliverables
A validated plugin package or `BLOCKED` / `NOT_INVOKED` with evidence.

## Workflow
1. Confirm discovery evidence proves a real capability gap.
2. Choose the narrowest domain noun for plugin identity.
3. Resolve Plugin Creator as implementation authority.
4. Create the canonical plugin package without duplicating another agent/domain.
5. Validate the saved package and read it back before returning PASS.

## Validation
PASS requires a real saved package plus validation evidence. Creation intent or emitted routing is not execution.

## Pitfalls
Do not create duplicate domain agents, broaden the plugin beyond the proven gap, or treat package generation as marketplace membership.

## Resources
See `references/contract.md`, `assets/request.json`, and `scripts/validate.py`.
