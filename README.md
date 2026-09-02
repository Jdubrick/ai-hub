# AI Hub

This repository contains shared Codex development guidelines and reusable subagent definitions.

## Syncing Codex configuration

The scripts in `scripts/` install the repository's configuration in `~/.codex`. Both scripts resolve source files relative to their own location, so they can be invoked from any working directory. Replace `/path/to/ai-hub` in the examples with the path to this checkout.

### Sync the global guidelines

```bash
/path/to/ai-hub/scripts/sync-agents.sh
```

`sync-agents.sh` creates `~/.codex` when needed, then copies the top-level `AGENTS.md` to `~/.codex/AGENTS.md`. An existing destination file is overwritten.

### Sync the subagents

```bash
/path/to/ai-hub/scripts/sync-subagents.sh
```

`sync-subagents.sh` creates `~/.codex/agents` when needed, then copies the contents of this repository's `agents/` directory into it. Existing files with the same names are replaced, while files that exist only in `~/.codex/agents` are preserved.

## Reporting Codex usage

Run the local usage report with:

```bash
python3 /path/to/ai-hub/scripts/codex_usage.py
```

The script reads retained rollout files from `~/.codex/sessions` and `~/.codex/archived_sessions`. It attributes token deltas to the model active in each `turn_context`, so a conversation that switches models is split correctly. It buffers token counts that arrive before the first model context and assigns them to that model. If no model metadata is ever available, it reports the tokens separately as unattributed instead of inventing a model. It reports token totals, cache use, estimated cost, run type, agent role, daily totals, and the largest runs.

Useful filters include:

```bash
python3 /path/to/ai-hub/scripts/codex_usage.py --since 2026-09-01 --until 2026-09-02
python3 /path/to/ai-hub/scripts/codex_usage.py --exclude-thread THREAD_ID
python3 /path/to/ai-hub/scripts/codex_usage.py --codex-home /path/to/.codex
```

The cost output uses the standard short-context rates for GPT-5.6 Sol, Terra, and Luna embedded in the script. It is an estimate, not an account billing export, and excludes long-context multipliers and tool-specific charges.

## Included subagents

- **developer-simple** handles small, well-defined coding tasks where the intended solution is already clear. It focuses on the smallest complete change and validates its work.
- **developer-complex** takes on ambiguous or cross-cutting development work that requires investigation, architectural judgment, or changes across multiple components.
- **reviewer** performs a read-only review after implementation. It checks the completed work against its requirements and reports issues by severity, including concerns about correctness, tests, security, architecture, and documentation.
- **technical-writer** updates documentation after implementation. It keeps documentation aligned with the completed work, follows repository conventions, and favors concise, human-friendly wording.

To allow agents to run in parallel with the expected delegation depth, configure Codex with:

```toml
[agents]
max_threads = 6
max_depth = 1
```
