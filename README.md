# AXION B21 — Offensive Security Portfolio

Flask + PostgreSQL + Cloudinary. Every writeup, project, blog, research paper,
certification, and setting is editable from a hidden admin panel — data is
stored in PostgreSQL and files in Cloudinary, so **nothing is lost when the
server restarts** (unlike storing files directly on Render's disk, which wipes
on every restart).

## 1. Push to GitHub

Upload every file in this folder to the **root** of your repo — `app.py`
should sit directly at the top level, not nested inside another folder.

## 2. Create accounts you'll need

- [Render](https://render.com) — hosting + free PostgreSQL database
- [Cloudinary](https://cloudinary.com) — free file storage (find your
  Cloud Name, API Key, and API Secret on the Cloudinary dashboard home page)

## 3. Deploy on Render

1. New → Blueprint → connect your GitHub repo. Render reads `render.yaml`
   automatically and creates both the web service and the database.
2. Render will ask you to fill in the values marked `sync: false`:
   - `ADMIN_USER` — pick a username
   - `ADMIN_PASS` — pick a strong password
   - `ADMIN_URL_PATH` — a hard-to-guess path, e.g. `axen-ctrl-7f3q`
     (your admin panel will live at `/axen-ctrl-7f3q/login`, not `/admin`)
   - `CLOUDINARY_CLOUD_NAME`, `CLOUDINARY_API_KEY`, `CLOUDINARY_API_SECRET`
3. Deploy. Wait for the build to finish.

## 4. Create your admin account (one-time)

Render dashboard → your service → **Shell** tab → run:

```bash
flask --app app.py init-admin
```

This reads `ADMIN_USER` / `ADMIN_PASS` from your environment variables and
creates the account. Re-running it later does nothing if an admin already
exists (safety check).

## 5. Log in

Go to `https://your-app.onrender.com/<ADMIN_URL_PATH>/login` and log in.
From the dashboard you can create/edit/delete every section and upload
images, PDFs, and files — they go straight to Cloudinary.

## Local development

```bash
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env              # then fill in real values
flask --app app.py init-admin
python app.py
```

Site runs at `http://localhost:5000`.

## Notes / downsides to know

- **Free Render web services sleep after inactivity** — the first request
  after idle time takes ~30-50 seconds to wake up. Fine for a portfolio,
  just don't be surprised.
- **Cloudinary free tier** has a storage/bandwidth cap (~25GB). Images and
  PDFs are no problem; avoid uploading large videos repeatedly.
- To reset your admin password later: Render Shell tab, delete the old
  `AdminUser` row via `flask shell`, then run `init-admin` again.
