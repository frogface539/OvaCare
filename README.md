# 🌸 PCOS Care — Women’s Health Assistant

A friendly, end-to-end Women’s Health Assistant focused on PCOS (Polycystic Ovary Syndrome). This project combines a reproducible Random Forest risk model, a focused AI chatbot (Groq/OpenAI compatible), a period tracker, and a doctor contact directory — all wrapped in a clean, privacy-minded frontend and a lightweight FastAPI backend.

The aim: help people learn, triage, and prepare for conversations with healthcare providers — not to diagnose.

---

## 💡 Key Features

- Predictive model
  - Reproducible Random Forest classifier (training script included)
  - Saves artifacts: model, encoders, scaler, feature names
  - Produces probability-based risk score and top contributing features

- PCOS Expert Chatbot
  - Streamlit frontend + FastAPI backend integration
  - Backend can call Groq/OpenAI LLMs with a strict PCOS-only system prompt
  - Retrieval-first layer using curated FAQ for deterministic answers when possible
  - Returns structured response: assistant text, sources, confidence

- Utilities
  - Period Tracker (browser storage)
  - Doctor Directory (click-to-call/email)
  - UI-first Streamlit app for prediction, charts, and chatbot

- Developer-friendly
  - Modular frontend/backend separation
  - Docker-ready, simple deployment instructions
  - README, sample requests, and example backend for Groq included

---

## 🏗 Architecture (high level)

- Frontend: Streamlit app (UI for prediction, chatbot, tracker, directory)
- Backend: FastAPI
  - /chat -> handles chatbot requests, retrieves FAQ context, calls LLM
  - /predict -> loads model artifacts and returns risk probability + top features
- Model artifacts: stored under `models/` (joblib)
- Local data: `data.csv` (training / sample records)
- Optional: Docker containers for frontend/backend

---

## 🚀 Quickstart (developer)

Prereqs: Python 3.9+, git, (optional) Docker.

1. Clone
   ```bash
   git clone <repo-url>
   cd <repo>
   ```

2. Create a virtualenv and install requirements
   ```bash
   python -m venv .venv
   source .venv/bin/activate     # macOS / Linux
   .venv\Scripts\activate        # Windows PowerShell
   pip install -r requirements.txt
   ```

3. Environment variables
   - For LLM (Groq) integration set:
     - `GROQ_API_KEY=sk-...`
   - Example (Linux/macOS):
     ```bash
     export GROQ_API_KEY="sk-..."
     ```
     Windows PowerShell:
     ```powershell
     $env:GROQ_API_KEY="sk-..."
     ```

---

## ▶️ Run the backend (FastAPI)

Start the backend that serves both chat and prediction endpoints:

```bash
uvicorn pcos_backend_improved:app --reload --port 8000
```

Endpoints:
- `POST /chat` — accepts `{"messages": [...]}` (OpenAI-style). Returns:
  ```json
  { "assistant": "...", "sources": [...], "confidence": 0.85 }
  ```
- `POST /predict` — accepts user features JSON (see example below). Returns:
  ```json
  { "probability": 0.42, "risk_pct": 42.0, "top_features": [{"feature":"BMI","value":...}], "explanation": "..." }
  ```

Example `/chat` request:
```json
{
  "messages": [
    {"role": "system", "content": "Optional system prompt"},
    {"role": "user", "content": "What are common PCOS symptoms?"}
  ]
}
```

Example `/predict` request:
```json
{
  "features": {
    "Age": 27,
    "Height(cm)": 162,
    "Weight(kg)": 62,
    "BMI": 23.6,
    "Cycle Length(days)": 35,
    ...
  }
}
```

---

## ▶️ Run the frontend (Streamlit)

Start the Streamlit app (UI: chatbot, prediction form, tracker, doctors):
```bash
streamlit run app.py
```
- The app expects the backend at `http://localhost:8000` by default. You can change endpoints in the Streamlit config/constants.

---

## 🧪 Training & Model artifacts

- Training script: `train_pcos_realdata.py`  
  - Loads `data.csv`, preprocesses, trains RandomForestClassifier, evaluates, saves artifacts under `models/` using `joblib`.
- Recommended improvements for production:
  - Use StratifiedKFold cross-validation
  - Calibrate probabilities (CalibratedClassifierCV)
  - Hyperparameter tuning (RandomizedSearchCV / Optuna)
  - External validation on real clinical data
- After training you should have:
  - `models/model.pkl`
  - `models/encoders.pkl`
  - `models/scaler.pkl`
  - `models/feature_names.pkl`

The backend will load these artifacts and expose `/predict`.

---

## 📚 Curated FAQ & Retrieval

The backend includes a small curated FAQ (JSON/embedded list). When user queries closely match FAQ entries, the service returns short deterministic answers. Otherwise it appends FAQ snippets to the LLM prompt to ground responses.

Add vetted references to `FAQ_ITEMS` (in `pcos_backend_improved.py`) to improve correctness and traceability.

---

## 🔒 Privacy & Disclaimer

- This project is educational and supportive; it is NOT a medical diagnostic tool.
- Do not store personally identifiable information (PII) in logs.
- Display a clear disclaimer in the UI: recommend users consult a clinician for diagnosis or urgent concerns.

Suggested UI disclaimer:
> This tool provides risk estimations and educational content only. It is not a substitute for professional medical advice.

---

## 🐳 Docker (optional)

Example Dockerfiles are provided for frontend/backend. Basic commands:

```bash
# build backend
docker build -t pcos-backend -f Dockerfile.backend .
docker run -p 8000:8000 -e GROQ_API_KEY="sk-..." pcos-backend

# build frontend
docker build -t pcos-frontend -f Dockerfile.frontend .
docker run -p 8501:8501 pcos-frontend
```

Adjust CORS and allowed hosts for production.

---

## ✅ Testing & Validation

- Unit tests: model loading, `/predict` schema, `/chat` request handling.
- Manual validation: compare predicted probabilities with known cases or clinician feedback.
- Monitor drift and set alerts if the prediction distribution changes.

---

## 🙋 How your teammate can get started

1. Pull this repo.
2. Install requirements.
3. Set `GROQ_API_KEY`.
4. Run backend: `uvicorn pcos_backend_improved:app --reload --port 8000`.
5. Run frontend: `streamlit run app.py`.
6. Test endpoints with sample requests above.

If your teammate needs an offline demo without Groq, the backend has a deterministic FAQ fallback mode. Remove or limit LLM calls by setting `GROQ_API_KEY` to empty during demos.

---

## ✍️ Contributing

Contributions are welcome:
- Expand & vet FAQ items
- Add clinician-reviewed example cases
- Improve tests and CI
- Add deployment scripts (Kubernetes, Cloud Run, etc)

Please follow a simple PR workflow and include tests for code changes.

---

## 📞 Contact

Project maintained by: Lakshay Jain, Palak

---

Thank you — this project is designed to be practical, understandable, and safe. It helps people get informed and take the next step with a clinician. Good luck at the hackathon! 🚀
