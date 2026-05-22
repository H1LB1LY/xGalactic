# xGalactic — Grok-Powered Galactic Standard Translator

**The X-like translation experience your international Discord server deserves.**  
Powered by the same Grok that powers translation on X.

React with any flag emoji for an instant natural translation.  
Right-click any message → **Translate with Grok**.  
Or just type `/groktranslate`.

Built for international guilds, gaming communities, and Foundation-inspired servers.

---

### ✨ Key Features

- X-style on-demand translation (flags, context menu, slash command)
- Smart language onboarding with button panel + roles
- Clean channel visibility (language channels hidden from @everyone)
- Optional linked-channel auto-mirroring with webhooks
- Full admin control (per-server API key, budget cap, /stats)
- Production-ready security and rate limiting

---

### Quick Start (Local Testing)

#### 1. Create a Discord bot
1. Go to the [Discord Developer Portal](https://discord.com/developers/applications) → **New Application**
2. Go to **Bot** → click **Reset Token** → copy the `DISCORD_TOKEN`
3. Under **Privileged Gateway Intents**, enable **Message Content Intent** and **Server Members Intent**
4. Go to **OAuth2 → URL Generator**
   - Scopes: `bot` + `applications.commands`
   - Permissions: `Manage Roles`, `Manage Channels`, `Send Messages`, `Embed Links`, `Add Reactions`, `Manage Webhooks`, `Read Message History`
5. Copy the generated URL and invite the bot to your test server

#### 2. Get an xAI API key (admin only)
1. Go to [console.x.ai](https://console.x.ai/)
2. Sign in with your X account and create a new API key
3. Copy the key — only the server admin needs this

#### 3. Install & run locally
```bash
git clone https://github.com/YOURUSERNAME/xGalactic.git
cd xGalactic
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS / Linux

pip install -r requirements.txt
cp .env.example .env
```

Edit `.env` and paste your `DISCORD_TOKEN` and `XAI_API_KEY`.

Run the bot:
```bash
python main.py
```

#### 4. First-time server setup
- Place the **xGalactic** bot role **above** all language roles
- Run `/setup-welcome` in your onboarding channel
- Use `/create-language-role` and `/map-language-role`
- Use `/setup-channel-visibility` for language channels

---

### Important Role Hierarchy
```
@Moderator          ← global privilege (higher)
@Voice-User
@xGalactic          ← Bot role must be here
@Español            ← language roles (bot role ABOVE these)
@English
@everyone           ← hidden from language channels
```

- **Language roles** → view/send in language channels only
- **Global channels** → visible to everyone; use flag reactions for translation
- **Bot role** → must be above language roles for assignments & webhooks

---

## Commands

| Command | Who | Purpose |
|---------|-----|---------|
| `/groktranslate <text> [language]` | Everyone | Translate text with Grok |
| Right-click → **Translate with Grok** | Everyone | Translate a message |
| 🇪🇸 flag reaction | Everyone | Instant translation embed |
| `/setup-mirroring link` | Admin | Link channels for auto-translation |
| `/setup-welcome` | Admin | Post language selection panel |
| `/map-language-role` | Admin | Map language key → Discord role |
| `/setup-channel-visibility` | Admin | Hide channel from @everyone |
| `/config api-key` | Admin | Set guild xAI key |
| `/config model` | Admin | `grok-4.1-fast` or `grok-4.3` |
| `/config budget` | Admin | Monthly USD cap |
| `/stats` | Admin | Usage & estimated cost |

---

## Project Structure

```
xGalactic/
├── main.py              # Bot entry point
├── cogs/
│   ├── translation.py   # Reactions, context menu, /groktranslate
│   ├── mirroring.py     # Webhook channel mirroring
│   ├── onboarding.py    # Welcome panel & roles
│   ├── config.py        # Admin configuration
│   └── stats.py         # Usage & billing stats
├── utils/
│   ├── db.py            # SQLite persistence
│   ├── grok.py          # xAI Grok client
│   ├── flags.py         # Flag → language mapping
│   ├── rate_limit.py    # Per-guild/user limits
│   ├── embeds.py        # X-style embeds
│   ├── security.py      # Input sanitization
│   └── helpers.py       # Shared cog helpers
├── .env.example
├── Dockerfile
└── docker-compose.yml
```

---

### Cost & Billing

- **100% admin responsibility** — one xAI key per server (or global `.env` key)
- Pay-as-you-go Grok tokens (linear scaling, no thresholds)
- Typical active server: $2–12/month on grok-4.1-fast
- `/stats` — requests, tokens, estimated monthly USD
- `/config budget 50` — pause translations when ~$50/month estimated spend is reached

Pricing estimates use approximate xAI rates in code; update `utils/grok.py` and `utils/db.py` when xAI changes pricing.

---

### Security & License
- Fully self-hostable
- MIT — use freely, self-host, modify. Not affiliated with X or xAI.
- Keys only in environment variables or encrypted local SQLite (guild key via `/config`)
- Least-privilege intents (`message_content`, `members`, `reactions`)
- Per-guild + per-user rate limiting
- Input sanitization (4k char cap, control char strip)
- Webhook names sanitized
- No telemetry or external analytics


## Deployment

### Railway

1. Push this repo to GitHub
2. [railway.app](https://railway.app) → **New Project** → **Deploy from GitHub**
3. **Variables** tab:
   - `DISCORD_TOKEN`
   - `XAI_API_KEY`
   - `GROK_MODEL=grok-4.1-fast`
4. Add a **Volume** mounted at `/app/data` for SQLite persistence
5. Start command: `python main.py`

### Replit

1. Import repo → **Secrets**: `DISCORD_TOKEN`, `XAI_API_KEY`
2. Run: `pip install -r requirements.txt && python main.py`
3. Use **Always On** (paid) for 24/7 uptime
4. Store `data/` in Replit object storage or external DB for persistence

### Docker (VPS / any host)

```bash
cp .env.example .env
# Edit .env
docker compose up -d --build
docker compose logs -f
```

### VPS (Ubuntu)

```bash
sudo apt update && sudo apt install -y python3.12 python3.12-venv git
git clone <repo> /opt/xgalactic && cd /opt/xgalactic
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env && nano .env

# systemd service
sudo tee /etc/systemd/system/xgalactic.service << 'EOF'
[Unit]
Description=xGalactic Discord Bot
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/opt/xgalactic
EnvironmentFile=/opt/xgalactic/.env
ExecStart=/opt/xgalactic/.venv/bin/python main.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl enable --now xgalactic
```



--

## Environment Variables

| Variable | Required | Default |
|----------|----------|---------|
| `DISCORD_TOKEN` | Yes | — |
| `XAI_API_KEY` | Yes* | — |
| `GROK_MODEL` | No | `grok-4.1-fast` |
| `DATABASE_PATH` | No | `data/xgalactic.db` |
| `RATE_LIMIT_GUILD` | No | `60`/min |
| `RATE_LIMIT_USER` | No | `10`/min |

\* Can be set per-guild via `/config api-key` instead.

---


Made for the Galactic Empire (and your Foundation guild) 🌌
