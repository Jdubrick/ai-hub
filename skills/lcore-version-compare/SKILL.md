---
name: lcore-version-compare
description: Compare Lightspeed Core (LCORE) versions. Use when asked to compare LCORE releases or identify differences between versions.
---

# Instructions

## Prerequisites

When using this skill it is important to clarify with the user which 2 Lightspeed Core (LCORE) versions to compare. In addition to the LCORE versions, you should request from the user the applicable Intelligent Assistant (or Lightspeed, depending on release) plugin. This ensures you can appropriately compare LCORE changes against the plugin that consumes the LCORE API. 

## Steps

1. Checkout both Lightspeed Core (LCORE) versions, for cheap exploration it is recommended to use more efficient subagents, like Luna.
2. Compare the source code between the two LCORE versions for important changes.
3. Compare the found changes against the given Intelligent Assistant (or Lightspeed) plugin to identify any areas that may be impacted.
4. Provide the user a summary report of LCORE changes and what, if any, impacts the plugin.

## Guidance

1. If unsure about any step in the process, confirm with the human.
2. Do not make any code changes, this is purely investigative.

