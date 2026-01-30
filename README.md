# Pip Face - Agent Project

Personal voice avatar agent integrated with Clawdbot messaging platform.

## Quick Start

See `STRUCTURE.md` for a complete map of where everything is.

**Key Locations:**
- **Source Code:** `./src/` — All Python modules
- **Scripts:** `./scripts/` — Bash/shell automation
- **Documentation:** `./docs/` — Setup and technical guides
- **Configuration:** `./config/` — systemd services, cron jobs
- **Assets:** `./assets/` — Images and avatars
- **Logs:** `./logs/` — Runtime output and debug logs
- **Memory:** `./memory/` — Daily notes and long-term memory (not in git)

## For Pip (The Agent)

Every session, load these files first:
- `SOUL.md` — Who you are
- `AGENTS.md` — Workspace rules
- `USER.md` — Who is Nilson
- `MEMORY.md` — Long-term memory
- `HEARTBEAT.md` — Periodic checks

Then check `STRUCTURE.md` to navigate the rest.

## Git Structure

Only project code is in git (src/, scripts/, docs/, config/, assets/).

Personal files are in `.gitignore`:
- Agent config (SOUL.md, AGENTS.md, etc.)
- Memory and logs (memory/, logs/)
- Backups and system files

This keeps the repo clean and shareable.

---

**Updated:** 2026-01-30
**Organization:** Agent-friendly, session-independent structure
