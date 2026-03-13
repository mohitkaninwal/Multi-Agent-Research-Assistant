# AutoResearch Frontend

Next.js frontend for AutoResearch. The UI is intentionally deployed separately from the FastAPI backend.

## Run locally

```bash
npm install
cp .env.example .env.local
npm run dev
```

Set `NEXT_PUBLIC_BACKEND_BASE_URL` if the backend is not running on `http://localhost:8000`.
