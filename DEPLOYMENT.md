# Deployment Guide for Hallucination Detector

This guide provides end-to-end instructions for deploying the **LLM Hallucination Detector** to production.

---

## Table of Contents
1. [Streamlit Community Cloud (Recommended & Free)](#1-streamlit-community-cloud)
2. [Hugging Face Spaces (Free)](#2-hugging-face-spaces)
3. [Render (Free / Paid)](#3-render)
4. [Railway (Usage-based)](#4-railway)
5. [Docker & Container Platforms (GCP Cloud Run, AWS ECS, DigitalOcean)](#5-docker--container-platforms)
6. [Troubleshooting & FAQs](#6-troubleshooting--faqs)

---

## 1. Streamlit Community Cloud
*Fastest deployment option. Free hosting directly from your GitHub repository.*

### Steps:
1. **Initialize Git & Push to GitHub**:
   ```bash
   git init
   git add .
   git commit -m "feat: ready for production deployment"
   git branch -M main
   git remote add origin https://github.com/<your-username>/<your-repo-name>.git
   git push -u origin main
   ```
2. **Go to Streamlit Cloud**:
   - Navigate to [share.streamlit.io](https://share.streamlit.io) and log in.
   - Click **Create App** (or **New App**).
3. **Configure Settings**:
   - **Repository**: `<your-username>/<your-repo-name>`
   - **Branch**: `main`
   - **Main file path**: `app.py`
4. **Configure Secrets**:
   - Click **Advanced Settings**.
   - Under **Secrets**, add:
     ```toml
     GROQ_API_KEY = "gsk_your_actual_groq_api_key_here"
     ```
5. Click **Deploy!**
   - Streamlit Cloud will install dependencies from `requirements.txt` and launch the app in 1–2 minutes.

---

## 2. Hugging Face Spaces
*Ideal for AI & ML communities.*

### Steps:
1. Go to [huggingface.co/spaces](https://huggingface.co/spaces) and click **Create new Space**.
2. **Space Details**:
   - Space Name: `hallucination-detector`
   - License: `mit`
   - Space SDK: **Streamlit**
   - Hardware: CPU basic (Free)
3. **Push Code to Space**:
   - Follow Hugging Face's instructions to clone the Space repo, copy this project's files into it, and push:
     ```bash
     git remote add space https://huggingface.co/spaces/<your-hf-username>/<your-space-name>
     git push space main
     ```
4. **Add Secret**:
   - In your Space, go to **Settings** -> **Variables and secrets**.
   - Under **Secrets**, add a new secret:
     - Name: `GROQ_API_KEY`
     - Value: `gsk_your_actual_groq_api_key`
5. The Space will automatically build and go live.

---

## 3. Render
*Great for web services with automated CI/CD.*

### Steps:
1. Log in to [dashboard.render.com](https://dashboard.render.com).
2. Click **New +** -> **Web Service**.
3. Connect your GitHub repository.
4. Set the configuration:
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `streamlit run app.py --server.port=$PORT --server.address=0.0.0.0`
5. Under **Environment Variables**, add:
   - Key: `GROQ_API_KEY`
   - Value: `gsk_your_actual_groq_api_key`
6. Click **Create Web Service**.

---

## 4. Railway

### Steps:
1. Log in to [railway.app](https://railway.app).
2. Click **New Project** -> **Deploy from GitHub repo**.
3. Select your repository. Railway will detect the `Procfile` and `requirements.txt` automatically.
4. Go to **Variables** tab in your Railway service:
   - Add `GROQ_API_KEY` = `gsk_your_actual_groq_api_key`
5. Click **Deploy**. Under **Settings** -> **Networking**, click **Generate Domain** to get your public URL.

---

## 5. Docker & Container Platforms
*(Google Cloud Run, AWS App Runner / ECS, Azure App Service, DigitalOcean Droplet)*

### Local Build & Test:
```bash
docker build -t hallucination-detector .
docker run -p 8501:8501 -e GROQ_API_KEY="your_api_key" hallucination-detector
```

### Google Cloud Run Example:
```bash
# 1. Build and push image to Google Artifact Registry
gcloud builds submit --tag gcr.io/[PROJECT-ID]/hallucination-detector

# 2. Deploy to Cloud Run
gcloud run deploy hallucination-detector \
  --image gcr.io/[PROJECT-ID]/hallucination-detector \
  --platform managed \
  --port 8501 \
  --set-env-vars GROQ_API_KEY="[YOUR_API_KEY]" \
  --allow-unauthenticated
```

---

## 6. Troubleshooting & FAQs

### Q: What happens if `GROQ_API_KEY` is not provided in environment variables?
The app gracefully displays a warning banner informing the user that an API key is needed, and provides an input field in the sidebar where users or reviewers can enter their own free Groq API key securely for their session.

### Q: Why is `app.py` in both the root and `src/`?
Most hosting services (Streamlit Cloud, Hugging Face Spaces, Render) expect the entry file `app.py` in the repository root. The root `app.py` serves as a standard bridge to `src/app.py`, ensuring zero-configuration deployment regardless of the platform.

### Q: What port does the app run on?
- Streamlit default: `8501`
- On Render/Railway/Heroku: `$PORT` is dynamically injected via `Procfile`.
