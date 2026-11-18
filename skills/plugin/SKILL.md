---
name: plugin
description: Act as the plugin-domain router and enforce discover-before-create.
---
# plugin

## Purpose
Resolve plugin-level capability needs and reuse existing validated plugins before creation.

## When to Use
Use this capability when it is the narrowest resolved skill for the current request.

## When Not to Use
Do not duplicate an existing validated capability, broaden scope silently, or claim execution without evidence.

## Inputs
A bounded request, resolved target identity, authorization context, and applicable evidence.

## Deliverables
One concrete result or a BLOCKED/NOT_INVOKED disposition with evidence.

## Workflow
1. Resolve Agent -> Plugin -> Skill -> Function.
2. Emit the exact functionality before execution.
3. Invoke the actual available provider or capability.
4. The installed Hook Agent may autonomously apply applicable lifecycle functions above this target; this skill does not own lifecycle behavior.
5. Verify the result with evidence.

## Validation
A PASS requires actual evidence. A declared path or emitted invocation is not proof of execution.

For `/plugin:plugin:validate-package`, run `python3 -B scripts/validate_package.py /absolute/plugin-checkout`
with the `agentskills` CLI on PATH. Pass more checkout roots to check them in one run.
This checks the canonical manifest, its Codex projection, and portable skill structure.
It does not install plugins, run skill scripts, or test model behavior.

## Pitfalls
Emission is not invocation. Discovery is not authorization. Skills-only packaging does not itself create a runtime tool.

## Resources
See references/contract.md and assets/request.json.
