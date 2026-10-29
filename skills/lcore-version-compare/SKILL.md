---
name: lcore-version-compare
description: Compare two Lightspeed Core (LCORE) versions and identify if there may be potential issues for a given Intelligent Assistant (Lightspeed) plugin.
---

# Instructions

## Prerequisites

When using this skill it is important to know what 2 Lightspeed Core (LCORE) versions to compare. Additionally, to get the most out of this skill it is also important to know wihch Intelligent Assistant (Lightspeed) plugin to check against. This plugin interacts with LCORE and any change to LCORE could affect the plugin.

For local cases, if you do not have the LCORE and plugin versions, you can request that information from the user. If being used remotely, and requesting input from the user is not available, do not make any assumptions and do not proceed further.

## Guidance

1. If unsure about any step in the process, do not make assumptions.
2. Do not make any code changes, this is purely investigative.

## Steps

1. Checkout both Lightspeed Core (LCORE) versions.
2. Compare the source code between the two LCORE versions for important changes, taking note of any changes that may impact the plugin.
3. Provide a summary report of the LCORE changes and what, if any, impacts the plugin.
