# AutoResearch

AutoResearch is a multi-agent research assistant split into two deployable apps:

- `backend/`: FastAPI + LangGraph orchestration + Groq LLM + Tavily research tools
- `frontend/`: Next.js UI that consumes the backend over HTTP

This structure keeps deployment simple: the backend can run on Railway, Render, Fly, or a container platform, while the Streamlit frontend can be hosted separately on Streamlit Community Cloud or another lightweight app host.

## Architecture

Workflow:

1. `planner` breaks a user query into 3-5 sub-topics.
2. `searcher` retrieves evidence from Tavily for each sub-topic.
3. `summarizer` condenses the evidence into grounded summaries.
4. `critic` identifies contradictions or evidence gaps.
5. `writer` produces a structured markdown report with references.

The critic can send the graph back to the searcher for one bounded retry loop.

## Repo Layout

```text
backend/
  app/
    agents/
    graph/
    tools/
    utils/
  main.py
  run_api.py
  requirements.txt
frontend/
  app/
  package.json
  next.config.ts
AutoResearch_TodoList.md
```

## Local Development

Backend:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python run_api.py
```

Frontend:

```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

## Deployment Guidance

- Deploy `backend/` as an API service.
- Deploy `frontend/` as a separate Next.js app.
- Configure `NEXT_PUBLIC_BACKEND_BASE_URL` on the frontend to point to the deployed backend.
- Configure `GROQ_API_KEY`, `TAVILY_API_KEY`, and optional Langfuse keys only on the backend.

## Evaluation

Run the backend evaluation script:

```bash
cd backend
python -m app.utils.eval
```

This generates CSV output comparing the multi-agent pipeline against a single-agent baseline.
