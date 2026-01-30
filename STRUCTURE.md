# 🗂️ Pip Face - System Structure Map

## Quick Reference
- **Agent Config**: `~/.config/clawdbot/` (read-only — managed by Clawdbot)
- **Personal Files**: `/home/nl3mos/clawd/` (your workspace)
- **Memory**: `/home/nl3mos/clawd/memory/` (daily logs + long-term notes)
- **Source Code**: `/home/nl3mos/clawd/src/` (all Python)
- **Scripts**: `/home/nl3mos/clawd/scripts/` (bash/shell)
- **Documentation**: `/home/nl3mos/clawd/docs/` (setup guides, technical docs)
- **Config**: `/home/nl3mos/clawd/config/` (systemd services, cronjobs)
- **Assets**: `/home/nl3mos/clawd/assets/` (images, avatars)
- **Logs**: `/home/nl3mos/clawd/logs/` (runtime logs)
- **Backups**: `/home/nl3mos/clawd/backups/` (old configs/snapshots)

## Root Files (Agent Identity — Load Every Session)
These are **personal agent files**, NOT in git:
- `SOUL.md` — Who you are, how you behave
- `AGENTS.md` — Workspace rules, tool notes
- `USER.md` — Who is Nilson
- `IDENTITY.md` — Your avatar, name, emoji
- `TOOLS.md` — Camera names, SSH hosts, etc
- `MEMORY.md` — Long-term memory (human memories)
- `HEARTBEAT.md` — Periodic checks to run

## Directories

### `/src/` — All Python Code
- `pip_face_v04.py` — Main avatar/UI code
- `pip_clawdbot_integration.py` — Integration with Clawdbot
- `pip_face_integration.py` — Main integration module
- `pip_face_monitor.py` — Monitor/watchdog process
- `pip_face_debug.py` — Debug utilities
- `pip_message_hook.py` — Webhook for messages
- `pip_clawdbot_hook.py` — Clawdbot hook integration
- `pip_message_interceptor.py` — Intercepts messages
- `pip_responder_interceptor.py` — Response interception
- `pip_response_middleware.py` — Response processing
- `pip_send_message.py` — Send messages

### `/scripts/` — Shell Scripts
- `pip_autostart.sh` — Start pip on boot
- `pip_keep_alive.sh` — Keep pip running (watchdog)
- `maintenance.sh` — Maintenance tasks
- `self_care.sh` — Self-healing routines
- `util_check.sh` — System checks

### `/docs/` — Documentation
- `PIP_AUTOSTART_SETUP.md` — Autostart config
- `PIP_FACE_SETUP.md` — Setup guide
- `PIP_INTEGRATION_COMPLETE.md` — Integration docs

### `/config/` — Configuration Files
- `pipface.service` — Systemd service file
- `maintenance_cron` — Cron schedule
- `maintenance_schedule` — Schedule definition

### `/assets/` — Images/Media
- `pip_avatar_idle.png` — Idle state
- `pip_avatar_talking.png` — Talking state
- `pip_v2_idle.png` — V2 variant
- `pip_v2_falando.png` — V2 talking

### `/memory/` — Daily Logs + Long-term Notes
- `2026-01-DD.md` — Daily session notes (raw)
- `credentials.md` — Private credentials reference

### `/logs/` — Runtime Output
- `pip_face.log` — Main process log
- `maintenance.log` — Maintenance log
- `security_alerts.log` — Security events
- `maintenance_report.txt` — Reports

### `/backups/` — Old Snapshots
Date-stamped snapshots of configs/memory from older sessions.

## Key Points
1. **Root stays clean** — Only personal agent files + this map
2. **Source in `/src/`** — Find all code in one place
3. **Logs segregated** — Check `/logs/` for debugging
4. **Scripts isolated** — `/scripts/` for all shell stuff
5. **Docs organized** — `/docs/` for setup/technical info
6. **Assets clear** — `/assets/` for all images

## How to Navigate
- Looking for a bug? Check `/src/` + `/logs/`
- Need to change startup? Edit `/config/pipface.service`
- Want to add a script? Create in `/scripts/`
- Documenting something? Add to `/docs/`
- Need a config file? Look in `/config/`

