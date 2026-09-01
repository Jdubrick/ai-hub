# Codex Subagents

## Prerequisites

Ensure that Agents in your Codex setup can run in parallel and have the proper depth set:



```toml 
~/.codex/config.toml
---
[agents]
max_threads = 6
max_depth = 1
```