# Daily Faceless Shorts Automation (100% Free)

Every day this pipeline automatically:
1. Picks a topic (rotates: motivation, facts/trivia, finance/tech tips)
2. Writes a script with a **free** LLM (Groq)
3. Converts it to speech with a **free** TTS voice (edge-tts)
4. Grabs matching **free** stock footage (Pexels)
5. Assembles a captioned vertical video (MoviePy, runs locally in CI — free)
6. Uploads it to YouTube (**free** API quota, ~6 uploads/day allowed)
7. Runs automatically every day via **GitHub Actions** (free for public repos,
   2,000 free minutes/month for private repos — this job takes ~5-10 min/day)

No paid subscriptions required anywhere in this pipeline.

---

## 1. Get your free API keys

### Groq (script writing)
1. Go to https://console.groq.com → sign up free → API Keys → Create key.
2. Copy it — you'll add it as a GitHub secret below.

### Pexels (stock footage)
1. Go to https://www.pexels.com/api/ → sign up free → get your API key.
2. Copy it.

### YouTube (upload)
This needs a one-time login on your own computer (Google requires a human
to approve access once — after that it renews automatically forever).

1. Go to https://console.cloud.google.com → create a new project.
2. In "APIs & Services" → "Library", enable **YouTube Data API v3**.
3. In "APIs & Services" → "Credentials" → "Create Credentials" →
   "OAuth client ID" → Application type: **Desktop app**.
4. Download the JSON, rename it `client_secret.json`.
5. On your own machine (not in CI):
   ```
   pip install google-auth-oauthlib
   python src/get_refresh_token.py
   ```
   This opens a browser — log in with the YouTube channel you want to post
   to, approve access. It will print:
   ```
   YT_CLIENT_ID     = ...
   YT_CLIENT_SECRET = ...
   YT_REFRESH_TOKEN = ...
   ```
   Save these three values.

> Note: Google's OAuth consent screen may show an "unverified app" warning
> since this is your own personal script — click "Advanced" → "Go to
> [app name] (unsafe)" to proceed. This is normal for personal-use apps and
> doesn't require Google's review process as long as you keep it in
> "Testing" mode with your own account added as a test user.

---

## 2. Push this project to a GitHub repo

```
git init
git add .
git commit -m "daily shorts automation"
git remote add origin <your-repo-url>
git push -u origin main
```

## 3. Add your secrets to GitHub

Repo → Settings → Secrets and variables → Actions → New repository secret.
Add all five:
- `GROQ_API_KEY`
- `PEXELS_API_KEY`
- `YT_CLIENT_ID`
- `YT_CLIENT_SECRET`
- `YT_REFRESH_TOKEN`

## 4. Turn it on

The workflow in `.github/workflows/daily.yml` runs automatically every day
at 14:00 UTC. Adjust the cron schedule to whatever time you like
(https://crontab.guru is handy for this).

You can also trigger it manually anytime: repo → Actions tab →
"Daily YouTube Short" → "Run workflow".

---

## Customizing

- **Topics/niches**: edit `TOPICS` in `config.py`.
- **Voice**: change `TTS_VOICE` in `config.py` — run `edge-tts --list-voices`
  locally to see all free options (many languages/accents).
- **Video length/style**: adjust `TARGET_DURATION_SECONDS`, `FONT_SIZE`, etc.
  in `config.py`.
- **Posting time**: edit the `cron` line in `.github/workflows/daily.yml`.
- **Privacy**: uploads default to `public`. Change `privacyStatus` in
  `src/upload_youtube.py` to `"private"` or `"unlisted"` if you want to
  review before publishing.

## Costs & limits to be aware of

- **Groq free tier**: generous daily request limits, plenty for 1 script/day.
- **Pexels free tier**: 200 requests/hour — this pipeline uses a handful/day.
- **YouTube API free quota**: 10,000 units/day, an upload costs ~1,600 units,
  so you can safely run this once (or a few times) a day without hitting limits.
- **GitHub Actions**: free minutes are generous for a job that runs once a
  day for a few minutes; keep the repo public for unlimited free minutes,
  or check your plan's private-repo minute allowance.

## Troubleshooting

- If captions fail to render, it's usually ImageMagick's security policy
  blocking text rendering — the workflow already patches this, but if
  running locally on Linux you may need the same `policy.xml` tweak.
- If uploads fail with an auth error, your refresh token may have been
  revoked — rerun `get_refresh_token.py` and update the GitHub secret.
