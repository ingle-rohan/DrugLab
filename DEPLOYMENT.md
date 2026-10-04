# DrugLab / DrugPedia - Deployment Guide

This guide covers how to deploy DrugLab to the public internet so anyone worldwide can visit and use the application.

---

## Architecture Overview

DrugLab is architected for unified full-stack serving:
1. **Frontend:** React 19 + TypeScript + Vite + Tailwind CSS. Compiled into `frontend/dist/`.
2. **Backend:** FastAPI (Python 3.11) with pgvector RAG provenance engine.
3. **Database:** Neon PostgreSQL with `pgvector` (already hosted in the cloud on AWS Singapore region).
4. **Unified Serving:** FastAPI mounts `frontend/dist/` at `/`, so **one single web service** serves the UI, the REST API (`/api/v1/*`), and the Swagger documentation (`/docs`) with zero CORS complications.

---

## Option 1: 1-Click Cloud Deployment on Render.com (Recommended & Free)

Render provides free cloud hosting with automatic HTTPS and continuous deployment from GitHub.

### Step 1: Push Project to GitHub
1. Create a new repository on [GitHub](https://github.com/new) named `DrugLab`.
2. In your local terminal, initialize git and push:
```bash
git init
git add .
git commit -m "Initial DrugLab full-stack commit"
git branch -M main
git remote add origin https://github.com/<your-username>/DrugLab.git
git push -u origin main
```

### Step 2: Deploy on Render
1. Go to [Render Dashboard](https://dashboard.render.com/) and click **New +** -> **Web Service**.
2. Connect your GitHub repository `DrugLab`.
3. Choose **Docker** as the Environment (it will automatically detect our `Dockerfile`).
4. Set the **Region** to `Singapore` (closest to our Neon database).
5. Choose the **Free** instance type.
6. Under **Environment Variables**, add:
   - `DATABASE_URL`: `postgresql://neondb_owner:npg_g0hZ5LSmjPqK@ep-jolly-bonus-b3ccfxu6.c-4.ap-southeast-1.aws.neon.tech/neondb?sslmode=require`
   - `ENVIRONMENT`: `production`
   - `EMBEDDING_MODEL`: `druglab-vector-v1`
7. Click **Create Web Service**.

Render will automatically build the container and provide your live public URL:
`https://druglab.onrender.com`

---

## Option 2: Deploy on Railway.app

Railway provides ultra-fast Docker deployments:
1. Go to [railway.app](https://railway.app) and click **New Project** -> **Deploy from GitHub repo**.
2. Select `DrugLab`.
3. Under **Variables**, add:
   - `DATABASE_URL`: `postgresql://neondb_owner:npg_g0hZ5LSmjPqK@ep-jolly-bonus-b3ccfxu6.c-4.ap-southeast-1.aws.neon.tech/neondb?sslmode=require`
4. Under **Settings** -> **Networking**, click **Generate Domain**.
5. Your app is live at `https://druglab.up.railway.app`.

---

## Option 3: Deploy on Koyeb or Fly.io

Koyeb offers free container hosting without sleep delays:
1. Connect GitHub repo on [koyeb.com](https://www.koyeb.com).
2. Select **Dockerfile** builder.
3. Add `DATABASE_URL` environment variable.
4. Deploy to get a permanent `https://<app>.koyeb.app` URL.

---

## Option 4: Local Docker Container

To run the production container locally:
```bash
docker build -t druglab:latest .
docker run -p 8000:8000 -e DATABASE_URL="postgresql://neondb_owner:npg_g0hZ5LSmjPqK@ep-jolly-bonus-b3ccfxu6.c-4.ap-southeast-1.aws.neon.tech/neondb?sslmode=require" druglab:latest
```
Visit `http://localhost:8000` to access the full application.

---

## Option 5: Instant Live Internet Access (Testing Right Now)

Your local instance is currently connected to a live public tunnel:
- **Public URL:** [https://six-buckets-sleep.loca.lt](https://six-buckets-sleep.loca.lt)
- **Tunnel Password / IP:** `223.238.138.139` (enter this if prompted by localtunnel verification).
