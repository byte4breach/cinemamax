# CinemaMax — Render.com Deployment Guide

**GitHub repo:** `https://github.com/byte4breach/cinemamax`  
**Services to deploy:** Java Spring Boot API · Python Telegram Bot · PostgreSQL DB

---

## Overview

Your project deploys **3 things** on Render:

| Service | Type | What it does |
|---------|------|-------------|
| `cinemamax-db` | PostgreSQL | Stores movies, showtimes, bookings |
| `cinemamax-api` | Docker (Java) | REST API, serves the web frontend |
| `cinemamax-bot` | Python web service | Telegram bot |

Your `render.yaml` already has all of this configured. You just need to connect it once and add secrets.

---

## Step 1 — Push Your Code to GitHub

> Skip if your repo at `github.com/byte4breach/cinemamax` is already up to date.

```bash
git add .
git commit -m "ready for render deploy"
git push origin main
```

---

## Step 2 — Create a Render Account & Connect GitHub

1. Go to **[render.com](https://render.com)** → **Get Started for Free**
2. Sign up (use GitHub login for easiest setup)
3. When prompted, **authorize Render** to access your GitHub account
4. Allow access to the `cinemamax` repository (or all repos)

---

## Step 3 — Deploy via render.yaml (Blueprint)

This is the fastest method — one click deploys all 3 services at once.

1. In the Render Dashboard, click **New → Blueprint**
2. Select your **`byte4breach/cinemamax`** repository
3. Render detects `render.yaml` automatically
4. Click **Apply**

Render will create:
- ✅ PostgreSQL database `cinemamax-db`
- ✅ Docker web service `cinemamax-api`
- ✅ Python web service `cinemamax-bot`

---

## Step 4 — Set the Bot Token Secret

The `BOT_TOKEN` is marked `sync: false` in `render.yaml` — you must add it manually.

1. In the Render Dashboard, go to **cinemamax-bot → Environment**
2. Add:
   - **Key:** `BOT_TOKEN`
   - **Value:** your Telegram bot token from [@BotFather](https://t.me/BotFather)
3. Click **Save Changes** → Render restarts the bot automatically

---

## Step 5 — Verify the Database URL is Wired Correctly

Render auto-injects `DATABASE_URL` from the database into `cinemamax-api`.

Your `application.properties` expects it like this:
```
spring.datasource.url=jdbc:${DATABASE_URL}
```

⚠️ **Important:** Render's `DATABASE_URL` starts with `postgres://...` but Spring Boot needs `postgresql://...`. Your current config uses `jdbc:${DATABASE_URL}` which means the URL becomes:

```
jdbc:postgres://user:pass@host/db
```

This may cause a connection error. Fix it by changing `application.properties`:

**Find this line:**
```properties
spring.datasource.url=jdbc:${DATABASE_URL}
```

**Replace with:**
```properties
spring.datasource.url=jdbc:postgresql://${DB_HOST}:${DB_PORT}/${DB_NAME}
spring.datasource.username=${DB_USER}
spring.datasource.password=${DB_PASSWORD}
```

**Then in Render Dashboard → cinemamax-api → Environment**, add these variables (get the values from **cinemamax-db → Info** in Render):

| Key | Where to find it |
|-----|-----------------|
| `DB_HOST` | Internal Database Hostname |
| `DB_PORT` | `5432` (always) |
| `DB_NAME` | `cinema_db` |
| `DB_USER` | `cinemamax` |
| `DB_PASSWORD` | Password shown in Render DB info |

**Alternatively** (simpler fix) — keep your current `application.properties` but add an env var in Render that transforms the URL. In `cinemamax-api → Environment`:

```
DATABASE_URL = postgresql://user:pass@host/db
```

(Copy the full Internal Connection String from Render DB and remove the `postgres://` prefix, replacing it with `postgresql://`)

---

## Step 6 — Set Up GitHub Actions Auto-Deploy (Optional but Recommended)

Your `.github/workflows/deploy.yml` is already written. You just need 3 secrets.

### Get the secrets:

**RENDER_API_KEY:**
1. Render Dashboard → top-right avatar → **Account Settings**
2. **API Keys → Create API Key**
3. Copy the key

**RENDER_API_SERVICE_ID** (for the Java API):
1. Go to `cinemamax-api` service in Render
2. Look at the URL: `https://dashboard.render.com/web/srv-XXXXXXXXXXXXXXXX`
3. Copy `srv-XXXXXXXXXXXXXXXX`

**RENDER_BOT_SERVICE_ID** (for the Python bot):
1. Same — go to `cinemamax-bot` service
2. Copy its `srv-XXXXXXXXXXXXXXXX` ID

### Add secrets to GitHub:
1. Go to `github.com/byte4breach/cinemamax`
2. **Settings → Secrets and variables → Actions → New repository secret**
3. Add all three:
   - `RENDER_API_KEY`
   - `RENDER_API_SERVICE_ID`
   - `RENDER_BOT_SERVICE_ID`

Now every `git push` to `main` auto-deploys both services. ✅

---

## Step 7 — First Deploy Checklist

After everything is set up, verify each part:

### Check the Java API:
Open: `https://cinemamax-api.onrender.com/api/movies`

You should see a JSON list of movies. If you see an error, check:
- Render Dashboard → `cinemamax-api` → **Logs**
- Most common issue: database URL format (see Step 5)

### Check the Web Frontend:
Open: `https://cinemamax-api.onrender.com/`

This serves the `index.html` from `src/main/resources/static/`.

### Check the Telegram Bot:
Send `/start` to your bot in Telegram. It should reply with a welcome message.

If the bot doesn't respond, check:
- `cinemamax-bot` → **Logs** in Render
- Make sure `BOT_TOKEN` is set correctly (Step 4)
- Make sure `API_BASE_URL` points to `https://cinemamax-api.onrender.com`

---

## Free Plan Limitations (Important!)

Render's free plan has one major caveat:

> **Services spin down after 15 minutes of inactivity.** The first request after sleeping takes ~30 seconds to wake up.

This affects both the API and the bot. For a production app, upgrade to the **Starter plan ($7/month per service)** or use an uptime pinger (e.g. [UptimeRobot](https://uptimerobot.com)) to ping `https://cinemamax-api.onrender.com/api/movies` every 14 minutes to keep it awake.

The **PostgreSQL free plan** is also limited to **90 days** on Render — after that you must recreate it or upgrade.

---

## Environment Variables Summary

### cinemamax-api
| Variable | Value | Source |
|----------|-------|--------|
| `DATABASE_URL` | auto-injected | Render DB |
| `CORS_ORIGINS` | `https://byte4breach.github.io` | render.yaml |
| `PORT` | auto-set by Render | Render |

### cinemamax-bot
| Variable | Value | Source |
|----------|-------|--------|
| `BOT_TOKEN` | your Telegram bot token | you add manually |
| `API_BASE_URL` | `https://cinemamax-api.onrender.com` | render.yaml |
| `WEB_APP_URL` | (optional) override the webapp URL | optional |

---

## Troubleshooting

**API returns 500 on first boot:**
The schema.sql runs automatically. If the DB isn't ready yet, wait 1-2 minutes and retry.

**Bot keeps restarting:**
The Python bot uses `run_polling()` which is fine for Render web services. If Render can't find a bound port, it will restart. The bot doesn't bind a port by default — you may need to add a simple health-check HTTP server. Add this to `bot.py`:

```python
# Add at the top
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

class Health(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")
    def log_message(self, *args): pass

def run_health():
    port = int(os.environ.get("PORT", 8080))
    HTTPServer(("0.0.0.0", port), Health).serve_forever()

# In main(), before app.run_polling():
threading.Thread(target=run_health, daemon=True).start()
```

**CORS errors from Telegram WebApp:**
Your `WebConfig.java` already uses `allowedOriginPatterns("*")` for `/api/**` so this should not happen. If it does, check the API is fully deployed and not sleeping.

---

## Quick Reference URLs (after deploy)

- **API:** `https://cinemamax-api.onrender.com`
- **Web App:** `https://cinemamax-api.onrender.com/` (or `https://byte4breach.github.io/cinemamax/`)
- **Bot:** find via [@BotFather](https://t.me/BotFather) → your bot username
- **Render Dashboard:** `https://dashboard.render.com`
