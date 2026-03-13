# AutoResearch Backend

FastAPI service that runs a LangGraph research workflow with five agents:

- `planner`: decomposes the research question into focused sub-topics
- `searcher`: gathers evidence for each sub-topic via Tavily
- `summarizer`: compresses evidence into grounded summaries
- `critic`: flags contradictions and unsupported claims
- `writer`: compiles the final cited markdown report

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python run_api.py
```

## API

- `GET /health`
- `POST /research`
- `GET /research/stream?query=...`

## CLI

```bash
python main.py "What is quantum computing?"
```

## Notes

- Set `LLM_PROVIDER=openai` with `OPENAI_API_KEY`, or `LLM_PROVIDER=anthropic` with `ANTHROPIC_API_KEY`.
- Set `TAVILY_API_KEY` to enable live web research.
- Set Langfuse credentials if you want traces and prompt observability.
