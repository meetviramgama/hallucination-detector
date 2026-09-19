---
title: LLM Hallucination Detector
emoji: 🛡️
colorFrom: blue
colorTo: indigo
sdk: streamlit
sdk_version: "1.35.0"
app_file: app.py
pinned: false
license: mit
---

# 🛡️ LLM Hallucination Detector

An automated AI fact-checking engine that evaluates LLM responses claim-by-claim against real-world knowledge from Wikipedia search snippets.

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.35+-red.svg)
![Groq](https://img.shields.io/badge/Groq-API-orange.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

---

## ⚡ How It Works

```
User Query
    ↓
1. Generator (openai/gpt-oss-20b via Groq)      → Full Answer
    ↓
2. Claim Extractor (openai/gpt-oss-20b via Groq)→ Atomic Factual Claims
    ↓
3. Evidence Retriever (Wikipedia Search API)   → Real-Time Evidence Snippets
    ↓
4. Claim Verifier (openai/gpt-oss-20b via Groq) → VERIFIED / FALSE / UNVERIFIED
    ↓
5. Trust Scorer (Deterministic Weighting)      → Trust Score (0–100) + Badge
```

---

## 🚀 Quick Local Setup

### 1. Clone the repository
```bash
git clone <your-repo-url>
cd hallucination-detector
```

### 2. Create and activate a virtual environment
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure API Key
Create a `.env` file in the root directory:
```bash
echo 'GROQ_API_KEY="your_groq_api_key_here"' > .env
```
*(Get a free Groq API key at [console.groq.com](https://console.groq.com/keys))*

### 5. Run the Streamlit Dashboard
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## 🌐 Deploying to the Cloud

For detailed deployment guides across all platforms, see [DEPLOYMENT.md](DEPLOYMENT.md).

### Option 1: Streamlit Community Cloud (Recommended — Free & Fast)
1. Push this repository to GitHub.
2. Go to [share.streamlit.io](https://share.streamlit.io) and log in with GitHub.
3. Click **New App** and choose your repository.
4. Set Main file path to: `app.py`.
5. Under **Advanced Settings** -> **Secrets**, add:
   ```toml
   GROQ_API_KEY = "gsk_your_groq_api_key"
   ```
6. Click **Deploy**!

### Option 2: Hugging Face Spaces (Free)
1. Create a new Space on [Hugging Face](https://huggingface.co/spaces) with **Streamlit** SDK.
2. Push this repo to your Space repository.
3. In Space **Settings** -> **Variables and secrets**, add `GROQ_API_KEY` as a Secret.
4. Your Space will build and launch automatically.

### Option 3: Docker Container
```bash
# Build the container
docker build -t hallucination-detector .

# Run with environment variable
docker run -p 8501:8501 -e GROQ_API_KEY="your_groq_api_key" hallucination-detector
```

Or using Docker Compose:
```bash
GROQ_API_KEY="your_key" docker compose up --build
```

### Option 4: Render / Railway / Heroku
The included `Procfile` and `runtime.txt` automatically handle port binding (`$PORT`) and environment configuration:
- Build command: `pip install -r requirements.txt`
- Start command: `streamlit run app.py --server.port=$PORT --server.address=0.0.0.0`
- Environment variables: Set `GROQ_API_KEY` in the service dashboard.

---

## 📁 Project Structure

```
hallucination-detector/
├── app.py                     # Root entry point for cloud deployments
├── requirements.txt           # Production dependencies
├── Dockerfile                 # Docker container image specification
├── docker-compose.yml         # Container orchestration
├── Procfile                   # Process file for Render / Railway / Heroku
├── runtime.txt                # Python runtime version definition
├── .dockerignore              # Excluded container build files
├── .gitignore                 # Excluded git tracking files
├── .streamlit/
│   ├── config.toml            # Production Streamlit UI & server configuration
│   └── secrets.toml.example   # Secrets template
├── src/
│   ├── app.py                 # Main Streamlit UI & interactive dashboard
│   ├── groq_client.py         # Groq LLM client wrapper (env + secrets aware)
│   ├── pipeline/              # Orchestration pipeline
│   ├── extractor/             # Atomic claim extraction
│   ├── retriever/             # Wikipedia evidence retrieval
│   ├── verifier/              # Evidence-based claim verification
│   ├── scorer/                # Trust scoring engine
│   └── eval/                  # Benchmark & evaluation tools
└── DEPLOYMENT.md              # Detailed step-by-step deployment guide
```

---

## 🔒 Security & Privacy

- `GROQ_API_KEY` is loaded dynamically from `os.environ`, `st.secrets`, or user session input.
- Secrets and `.env` files are ignored by git and excluded from Docker builds.
- If no server key is provided, the UI displays a secure sidebar input so users can bring their own keys without exposing them.
