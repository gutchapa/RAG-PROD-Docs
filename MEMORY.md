# Long-Term Memory

## 🛡️ Security Protocols (CRITICAL)
- **NO HARDCODED SECRETS:** Never write API keys, passwords, or tokens directly into code files (`.py`, `.js`, etc.) or `.env` files that might be committed.
- **Secrets Management:** Use OpenClaw's secret store (`openclaw config set secrets...`) or pass keys transiently via environment variables (`GOOGLE_API_KEY=... command`) only at runtime.
- **Leak Prevention:** If a key must be used, use it in-memory only. Do not persist it to disk in plaintext.

## Subagent Routing Setup

**Active Subagents (created 2026-02-27):**

| Agent | Role | Session Key |
|-------|------|-------------|
| **coding-agent** | Programming, debugging, code review | `agent:main:subagent:e87419c7-0166-446f-86cc-cac8045b2866` |
| **research-agent** | Web search, info gathering, fact-checking | `agent:main:subagent:4cb94324-1849-4062-bc09-57bc1dc1200a` |
| **booking-agent** | Reservations, appointments, calendar | `agent:main:subagent:d26060b2-418e-4d89-a068-2c790b2b749a` |
| **mundane-agent** | File organization, renaming, cleanup | `agent:main:subagent:0916b78b-9298-4d9e-b2ca-1233b8a3196d` |
| **dispatcher-agent** | Smart router for task allocation | `agent:main:subagent:7aa7aaec-9e36-46cf-af7a-237fe68fe9cd` |

**Routing Mode: Option B (Auto-Route)**
- All incoming messages are first analyzed by dispatcher-agent
- Dispatcher decides which specialist handles it
- Task is automatically forwarded to the appropriate agent
- User never sees the routing — just gets the result

**Gateway Health Check:**
- Script: `/root/.openclaw/scripts/gateway-health-check.sh`
- Cron: `*/2 * * * *` (every 2 minutes)
- Log: `/tmp/openclaw-gateway-monitor.log`
