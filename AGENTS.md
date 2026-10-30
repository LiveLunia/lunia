# Columbula Live — Development Rules

## Project
- Long-term personal project, maintained by one developer.
- Prefer simplicity, readability and maintainability.
- The developer is learning; explain non-obvious decisions.

## Architecture
- Columbula Core must remain independent of AstrBot.
- External platforms and games are replaceable integrations.
- Only one primary presence/activity may be active at a time.
- Reuse mature libraries instead of reinventing functionality.
- Do not implement features merely because they may be useful later.

## Coding
- Follow existing naming and formatting conventions.
- Prefer explicit data flow and small, cohesive modules.
- Avoid unnecessary abstraction, wrappers, factories and fallbacks.
- Validate external and security-sensitive inputs appropriately.
- Do not silently swallow exceptions.
- Do not refactor unrelated code.

## Testing
- Test according to actual risk and complexity.
- Reuse existing test files when appropriate.
- Prioritize game rules, hidden information and state transitions.
- Do not create redundant smoke, regression or baseline tests.
- Remove temporary debugging artifacts.

## Agent Behavior
- Do not start implementing code unless explicitly requested.
- For research tasks, analyze before recommending.
- Do not create excessive documents or directories.
- Explain tradeoffs and cite sources for technical claims.
- Keep changes limited to the requested scope.

## Documentation

- README.md and official project documentation use Simplified Chinese.
- AGENTS.md may use English.
- Code identifiers use English.
- Write temporary research reports to docs/research/.
- Write unfinished design proposals to docs/drafts/.
- Both directories are local-only and excluded from Git.
- Do not create progress logs, task summaries, or audit reports unless requested.
- Do not promote temporary documents to official documentation without approval.
- Keep documentation concise and avoid duplicating existing information.
- The ref/ directory contains third-party reference projects.
- Treat ref/ as read-only. Never modify, install, build, or test
  reference projects unless explicitly requested.