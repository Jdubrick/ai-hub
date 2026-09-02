# Global Development Guidelines

These are development guidelines intented to reduce common mistakes when working with agents. These are global defaults and project-specific AGENTS.md instructions take precedence when they are more specific or conflict with these guidelines.

## Guidelines
- Before making changes, inspect the repository structure and relevant instruction files, including nested AGENTS.md (or CLAUDE.md) files.
- Understand the requested outcome before making changes.
- Inspect existing code and conventions before introducing new patterns.
- Resolve minor ambiguity from available context when reasonable; surface assumptions when they materially affect the outcome.
- Prefer the simplest solution that fully solves the problem.
- Do not add speculative features, abstractions, or error handling.
- Keep changes focused on the assigned task and avoid unrelated refactoring.
- Reuse existing patterns, utilities, and dependencies when appropriate.
- Prefer fixing root causes over treating symptoms.
- Run relevant validation after making changes.
- Investigate failures rather than assuming they are unrelated.
- Review the final diff for accidental, unnecessary, or unrelated changes.
- Do not overwrite or discard existing user changes.

## Subagent Handling
- Do not spawn subagents when a single agent can complete the task effectively in one pass.
- Do not delegate merely to appear thorough or to increase parallelism.
- Use subagents when work can be cleanly decomposed into independent, focused tasks or when parallel investigation provides meaningful benefit.
- Give each subagent a narrowly scoped objective and explicit file ownership.
- Avoid assigning overlapping write scopes to parallel agents.
- Review and integrate subagent changes rather than assuming they are correct.