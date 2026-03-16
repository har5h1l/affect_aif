# Conductor Usage

## Quick Start

```bash
# single session (runs once, executes current MISSION.md)
./conductor/conductor.sh

# loop every 30 minutes (check in periodically)
./conductor/conductor.sh --loop 30m

# loop every 2 hours (longer autonomous runs)
./conductor/conductor.sh --loop 2h

# preview what would be sent to claude
./conductor/conductor.sh --dry-run

# use codex instead of claude for execution
./conductor/conductor.sh --codex-only
```

## Steering

Edit `conductor/MISSION.md` to change what the conductor does:
- Change **Tasks** to redirect work
- Change **Constraints** to add guardrails
- Set **Status** to `PAUSED` to stop the loop (resumes when changed back to `ACTIVE`)
- Add **Notes** for context the AI should know

## Monitoring

- `conductor/STATE.md` — current findings and experiment status (auto-updated)
- `conductor/log/` — full session transcripts
- `tail -f conductor/log/session_*.log` — watch current session

## On Oracle VM

```bash
# run via systemd
sudo cp conductor/conductor.service /etc/systemd/system/
sudo systemctl enable --now conductor.service

# check status
sudo journalctl -u conductor -f

# stop
sudo systemctl stop conductor
```

## Environment Variables

| Variable | Default | Purpose |
|---|---|---|
| `CONDUCTOR_CLAUDE_BIN` | `claude` | path to claude CLI |
| `CONDUCTOR_CODEX_BIN` | `codex` | path to codex CLI |
| `CONDUCTOR_CLAUDE_MODEL` | (default) | model override |
| `CONDUCTOR_MAX_TURNS` | `50` | max tool-use turns per session |

## Architecture

```
conductor/
├── MISSION.md        # you write this — the "system prompt"
├── STATE.md          # AI writes this — current findings
├── conductor.sh      # the loop
├── conductor.service # systemd unit for unattended VM operation
├── USAGE.md          # this file
└── log/              # session transcripts
```

The conductor is intentionally minimal. It:
1. Reads MISSION.md + STATE.md
2. Launches a Claude (or Codex) session with that context
3. The AI session has full tool access to run experiments, analyze, modify code
4. AI writes findings to STATE.md
5. Logs the full session transcript
6. Sleeps and repeats

No rigid pipeline. No behavioral gates. No scoring formulas.
The AI reads your instructions and does what you ask, like a conversation but automated.
