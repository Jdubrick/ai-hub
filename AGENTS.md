# Global Development Guidelines

These are development guidelines intented to reduce common mistakes when working with agents. These should be merged with project-specific instructions as required.

## Guidelines
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