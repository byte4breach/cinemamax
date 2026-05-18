# CinemaMax — Complete Deployment Guide
## From Zero to Live (GitHub → Render → Telegram)

---

## Architecture Overview

```
User (Telegram) ──► Python Bot ──► Java API ──► PostgreSQL DB
User (Browser)  ──────────────────► Java API ──► PostgreSQL DB
```

| Part | Language | Hosted on |
|------|----------|-----------|
| REST API + Web UI | Java (Spring Boot) | Render Web Service |
| Telegram Bot | Python | Render Worker |
| Database | PostgreSQL | Render Database |

---

## Step 1 — Create a GitHub Account & Repository

1. Go to **https://github.com** → Sign up (free)
2. Click **"New repository"** (green button, top-right)
3. Name it: `cinemamax`
4. Set it to **Public**
5. Click **"Create repository"**

---

## Step 2 — Install Git on Your Computer

### Windows:
- Download from **https://git-scm.com/download/win**
- Install with default options
- Open **Git Bash** (search in Start menu)

### Mac:
```bash
brew install git
```

### Check it works:
```bash
git --version
```

---

## Step 3 — Put Your Code on GitHub

Open Git Bash / Terminal in the project folder, then run these commands **one by one**:

```bash
# 1. Enter the project folder
cd cinemamax

# 2. Initialize git
git init

# 3. Tell git who you are (use your GitHub email)
git config user.name "Your Name"
git config user.email "you@example.com"

# 4. Add all files
git add .

# 5. Create the first commit
git commit -m "Initial commit: CinemaMax Java+Python project"

# 6. Connect to your GitHub repo (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/cinemamax.git

# 7. Push the code
git branch -M main
git push -u origin main
```

When you push again in the future (after making changes):
```bash
git add .
git commit -m "Describe what you changed"
git push
```
**That's it — Render will auto-deploy in ~2 minutes!**

---

## Step 4 — Create a Render Account

1. Go to **https://render.com** → Sign up with GitHub (easiest)
2. Authorize Render to access your GitHub account

---

## Step 5 — Deploy Everything on Render (Blueprint)

The `render.yaml` file in your repo tells Render exactly what to create.

1. In Render Dashboard → click **"New +"** → **"Blueprint"**
2. Connect your GitHub repo `cinemamax`
3. Render will read `render.yaml` and create:
   - ✅ PostgreSQL database (`cinemamax-db`)
   - ✅ Java Web Service (`cinemamax-api`)
   - ✅ Python Worker (`cinemamax-bot`)
4. **Before clicking Apply**, set the environment variable:
   - Service: `cinemamax-bot`
   - Key: `BOT_TOKEN`
   - Value: your Telegram bot token (see Step 6 below)
5. Click **"Apply"**

Wait ~5 minutes for first build (Java takes time to compile).

---

## Step 6 — Create a Telegram Bot

1. Open Telegram → search for **@BotFather**
2. Send: `/newbot`
3. Follow prompts → give it a name like "CinemaMax Bot"
4. BotFather will give you a token like: `1234567890:ABCdef...`
5. Copy this token → paste it as `BOT_TOKEN` in Render (Step 5 above)

To set the bot commands (optional but nice):
```
/setcommands → choose your bot → paste:
start - Book cinema tickets
```

---

## Step 7 — Set Up GitHub Auto-Deploy

This makes every `git push` automatically redeploy on Render.

### Get your Render API Key:
1. Render Dashboard → **Account Settings** → **API Keys**
2. Click **"Create API Key"** → copy it

### Get your Service IDs:
1. Go to your `cinemamax-api` service on Render
2. The URL looks like: `https://dashboard.render.com/web/srv-XXXXXXXX`
3. `srv-XXXXXXXX` is your **API service ID**
4. Repeat for `cinemamax-bot` → this is your **Bot service ID**

### Add secrets to GitHub:
1. Go to your GitHub repo → **Settings** → **Secrets and variables** → **Actions**
2. Add these 3 secrets:

| Secret Name | Value |
|-------------|-------|
| `RENDER_API_KEY` | Your Render API key |
| `RENDER_API_SERVICE_ID` | `srv-XXXX` for Java API |
| `RENDER_BOT_SERVICE_ID` | `srv-XXXX` for Python bot |

Now every time you push to `main`, both services redeploy automatically! 🎉

---

## Step 8 — Initialize the Database

On first deploy, Spring Boot auto-runs `schema.sql` which creates tables and sample data.

To verify:
1. Render Dashboard → `cinemamax-db` → **Connect** → copy the connection string
2. Or open the Render shell for `cinemamax-api` and test:
```bash
curl https://cinemamax-api.onrender.com/api/movies
```
You should see JSON with movie data!

---

## Step 9 — Test Everything

### Test the Web UI:
Open: `https://cinemamax-api.onrender.com`  
You should see the CinemaMax movie gallery.

### Test the API directly:
```
GET https://cinemamax-api.onrender.com/api/movies
GET https://cinemamax-api.onrender.com/api/movies/1/showtimes
GET https://cinemamax-api.onrender.com/api/showtimes/1/seats
```

### Test the Telegram Bot:
Open Telegram → search for your bot → send `/start`

---

## Daily Workflow (after setup)

```bash
# Make changes to any file
# Then:
git add .
git commit -m "What I changed"
git push
# Render auto-deploys in ~2 min — done!
```

---

## Project File Structure

```
cinemamax/
├── render.yaml                          ← Render deployment config
├── .gitignore
├── .github/
│   └── workflows/
│       └── deploy.yml                   ← GitHub Actions auto-deploy
│
├── java-backend/                        ← Spring Boot Java API
│   ├── pom.xml                          ← Maven dependencies
│   ├── mvnw                             ← Maven wrapper
│   └── src/main/
│       ├── java/com/cinemamax/
│       │   ├── CinemaMaxApplication.java  ← Entry point
│       │   ├── model/
│       │   │   ├── Movie.java
│       │   │   ├── Showtime.java
│       │   │   └── BookedSeat.java
│       │   ├── repository/
│       │   │   ├── MovieRepository.java
│       │   │   ├── ShowtimeRepository.java
│       │   │   └── BookedSeatRepository.java
│       │   ├── service/
│       │   │   └── CinemaService.java     ← Business logic
│       │   └── controller/
│       │       ├── CinemaController.java  ← REST API endpoints
│       │       └── WebConfig.java         ← CORS config
│       └── resources/
│           ├── application.properties     ← DB config, port
│           ├── schema.sql                 ← DB tables + sample data
│           └── static/
│               └── index.html             ← Web UI (your frontend)
│
└── python-bot/
    ├── bot.py                             ← Telegram bot (calls Java API)
    └── requirements.txt
```

---

## Key Java Concepts Used (for your assignment)

| Concept | Where used |
|---------|-----------|
| **Classes & Objects** | `Movie`, `Showtime`, `BookedSeat` model classes |
| **Inheritance** | Spring repositories extend `JpaRepository` |
| **Annotations** | `@Entity`, `@RestController`, `@Service`, `@Transactional` |
| **Generics** | `JpaRepository<Movie, Long>`, `List<MovieDTO>` |
| **Records** | `MovieDTO`, `ShowtimeDTO`, `BookingResult` (immutable data) |
| **Stream API** | `movies.stream().map(...).toList()` |
| **Interfaces** | Repository interfaces, `WebMvcConfigurer` |
| **Dependency Injection** | `@RequiredArgsConstructor`, Spring IoC container |
| **Exception Handling** | `NoSuchElementException`, try-catch in service |

---

## Troubleshooting

**Build fails on Render:**
- Check the build logs in Render dashboard
- Make sure `pom.xml` is in `java-backend/` folder

**Bot not responding:**
- Check the `cinemamax-bot` worker logs on Render
- Verify `BOT_TOKEN` env var is set correctly

**API returns 500 error:**
- Check `cinemamax-api` logs
- Verify `DATABASE_URL` is connected to the database

**"Free tier" sleeping:**
- Render free tier sleeps after 15 min of inactivity
- First request after sleep takes ~30 seconds to wake up
- This is normal on free tier

---

*CinemaMax — Java + Python + PostgreSQL + Render + Telegram*
