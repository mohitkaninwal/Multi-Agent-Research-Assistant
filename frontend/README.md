# AutoResearch Frontend

Streamlit app for the AutoResearch UI. This app is intentionally isolated from backend code so it can be deployed independently.

## Run locally

```bash
pip install -r requirements.txt
cp .env.example .env
streamlit run app.py
```

Set `BACKEND_BASE_URL` in `.env` if the backend is not running on `http://localhost:8000`.
