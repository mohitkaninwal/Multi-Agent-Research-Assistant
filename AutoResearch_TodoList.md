# 🔬 AutoResearch — Multi-Agent Research Assistant
### Build To-Do List
**Stack:** LangGraph · Python · Tavily API · Streamlit

---

## 📋 Project Overview

| Field | Details |
|-------|---------|
| **Goal** | Multi-agent system that takes a research question and produces a cited, structured report |
| **Agents** | Planner → Searcher → Summarizer → Critic → Writer |
| **Orchestration** | LangGraph (StateGraph with typed state) |
| **Search** | Tavily API (built for LLM agents) |
| **LLM** | Claude claude-sonnet-4-20250514 or GPT-4o via API |
| **Frontend** | Streamlit |
| **Deployment** | Hugging Face Spaces or Railway |
| **Est. Time** | 2–3 weekends |

---

## 🛠️ Phase 1 — Environment Setup *(Day 1, ~2 hrs)*

### 📁 Create project structure
- `mkdir autoResearch && cd autoResearch`
- Create folders: `agents/`, `graph/`, `tools/`, `utils/`, `frontend/`
- Create files: `main.py`, `config.py`, `requirements.txt`, `.env`, `README.md`
- `.gitignore`: add `.env`, `__pycache__`, `.venv`

### 🐍 Set up Python virtual environment
- `python -m venv .venv && source .venv/bin/activate`
- `pip install langgraph langchain langchain-anthropic tavily-python streamlit python-dotenv`

```txt
# requirements.txt
langgraph>=0.2.0
langchain>=0.3.0
langchain-anthropic>=0.2.0
tavily-python>=0.3.0
streamlit>=1.35.0
python-dotenv>=1.0.0
pydantic>=2.0.0
```

### 🔑 Configure API keys
- Get Tavily API key from [tavily.com](https://tavily.com) (free tier = 1000 searches/month)
- Get Anthropic API key from [console.anthropic.com](https://console.anthropic.com)
- Add both to `.env`:

```env
TAVILY_API_KEY=tvly-...
ANTHROPIC_API_KEY=sk-ant-...
```

> 💡 **Tip:** Test your keys early — run a simple Tavily search and a Claude API call before building agents.

---

## 🧩 Phase 2 — Define State & Graph Skeleton *(Day 1, ~2 hrs)*

### 📐 Define the shared `ResearchState` (TypedDict)
- Create `graph/state.py`
- Fields: `query`, `sub_topics`, `search_results`, `summaries`, `contradictions`, `final_report`, `current_step`
- This state flows through **ALL** agents — design it carefully

```python
# graph/state.py
from typing import TypedDict, List, Dict, Optional

class ResearchState(TypedDict):
    query: str
    sub_topics: List[str]
    search_results: Dict[str, List[dict]]
    summaries: Dict[str, str]
    contradictions: List[str]
    final_report: str
    current_step: str
```

### 🗺️ Create the LangGraph StateGraph skeleton
- Create `graph/graph.py`
- Instantiate `StateGraph(ResearchState)`
- Add placeholder nodes: `planner`, `searcher`, `summarizer`, `critic`, `writer`
- Define edges: `planner → searcher → summarizer → critic → writer → END`
- Compile the graph and test it runs without errors

> 💡 **Tip:** Use `add_conditional_edges` on the critic node later to loop back to searcher if contradictions are found.

---

## 🤖 Phase 3 — Build Each Agent *(Days 2–3, ~6 hrs)*

### Agent 1 — 📝 Planner (`agents/planner.py`)
- **Input:** `query` from state
- **Prompt:** *"Break this research question into 3–5 focused sub-topics"*
- **Output:** list of `sub_topics` → update state
- Use structured output (Pydantic model) for reliable parsing

### Agent 2 — 🔍 Searcher (`agents/searcher.py`)
- **Input:** `sub_topics` list from state
- For each sub-topic: call Tavily search API (`max_results=5`)
- Store results as dict keyed by sub-topic → update `state['search_results']`
- Handle API errors and empty results gracefully
- Add a small delay between calls to avoid rate limits

```python
# tools/tavily_search.py
from tavily import TavilyClient
import os

client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

def search(query: str, max_results: int = 5) -> list:
    response = client.search(query=query, max_results=max_results)
    return response.get("results", [])
```

### Agent 3 — ✂️ Summarizer (`agents/summarizer.py`)
- **Input:** `search_results` dict from state
- For each sub-topic: summarize its results into 2–3 sentences
- Prompt: include the sub-topic + raw snippets, ask for concise summary with key facts
- **Output:** `summaries` dict → update state

### Agent 4 — 🧐 Critic (`agents/critic.py`)
- **Input:** `summaries` dict from state
- **Prompt:** *"Review these summaries. Identify any factual contradictions or unsupported claims"*
- **Output:** list of `contradictions` → update state
- Add conditional edge: if contradictions found → loop back to searcher *(optional for v1)*

### Agent 5 — ✍️ Writer (`agents/writer.py`)
- **Input:** `query`, `sub_topics`, `summaries`, `contradictions` from state
- Prompt: compile a structured report with sections per sub-topic, intro, conclusion, caveats
- **Output:** `final_report` (markdown string) → update state
- Include source URLs from `search_results` in a **References** section

---

## 🔗 Phase 4 — Wire the Graph *(Day 3, ~2 hrs)*

### ⚡ Register all agent nodes in `graph.py`
- `graph.add_node('planner', planner_node)`
- `graph.add_node('searcher', searcher_node)`
- `graph.add_node('summarizer', summarizer_node)`
- `graph.add_node('critic', critic_node)`
- `graph.add_node('writer', writer_node)`
- Set entry point: `graph.set_entry_point('planner')`

### 🔄 Define edges and conditional routing
- Simple path: `planner → searcher → summarizer → critic → writer → END`
- Optional loop: critic checks contradictions → if found, goes back to searcher
- Use `add_conditional_edges` with a routing function on the critic node

### 🧪 Test the full pipeline end-to-end
- Run `main.py` with a test query: *"What is quantum computing?"*
- Print state at each step to verify data flows correctly
- Fix any state key mismatches between agents

> 💡 **Tip:** Use LangGraph's built-in `.get_graph().draw_mermaid()` to visualize your graph topology — great for your README!

---

## 🎨 Phase 5 — Streamlit Frontend *(Day 4, ~2 hrs)*

### 🖥️ Create `frontend/app.py`
- Text input for research query
- Submit button to invoke the LangGraph pipeline
- `st.status()` block to show live agent progress (Planner → Searcher → ...)
- Display final report as `st.markdown()`
- Sidebar: show sub-topics, sources, and any contradictions flagged

### ⚙️ Add streaming / step updates *(bonus)*
- Use LangGraph's `.stream()` instead of `.invoke()` to get per-step updates
- Push updates to Streamlit using `st.empty()` placeholders
- Show each agent completing in real time

```python
# frontend/app.py (skeleton)
import streamlit as st
from graph.graph import build_graph

st.title("🔬 AutoResearch")
query = st.text_input("Enter your research question")

if st.button("Research") and query:
    graph = build_graph()
    with st.status("Running agents...", expanded=True):
        for step in graph.stream({"query": query}):
            st.write(f"✅ {list(step.keys())[0]} complete")
    st.markdown(state["final_report"])
```

---

## 📊 Phase 6 — Evals & Quality *(Day 5, ~2 hrs)*

### 📏 Build a simple eval script (`utils/eval.py`)
- Define 5 test queries with known expected facts
- Run pipeline on each → check if final report contains expected facts
- Score: `facts_found / total_facts` → report coverage %
- Log results to a CSV for easy comparison

### 🏆 Baseline comparison *(bonus)*
- Run the same queries through a single-agent (no orchestration) version
- Compare output quality and coverage vs multi-agent version
- Include results in README as a table — very impressive for interviewers

> 💡 **Tip:** Even a basic eval script signals engineering maturity. Most candidates skip this step entirely.

---

## 🚀 Phase 7 — Deployment & Polish *(Day 6, ~2 hrs)*

### ☁️ Deploy to Hugging Face Spaces
- Create `requirements.txt` with pinned versions
- Create `app.py` at root (HF Spaces entry point)
- Add secrets in HF Spaces settings (API keys — **never commit to git!**)

### 📖 Write a strong `README.md`
- Add architecture diagram (use LangGraph's `draw_mermaid` output)
- Explain each agent's role in 1–2 sentences
- Include a demo GIF (record with LICEcap or Kap)
- Add eval results table comparing single-agent vs multi-agent
- Link to live demo and explain tech stack choices

### 🎯 Final polish for resume
- Add GitHub topics: `langgraph`, `multi-agent`, `rag`, `llm`, `research-assistant`
- Pin the repo on your GitHub profile
- Write a 2-line project summary for your resume bullet point
- Prepare a 2-minute explanation of your agent design decisions for interviews

> 💡 **Resume bullet:** *"Built a multi-agent research assistant using LangGraph with 5 specialized agents (Planner, Searcher, Summarizer, Critic, Writer), deployed on Hugging Face Spaces with a custom eval framework."*

---

## ⚡ Quick Reference — Files to Create

| File | Purpose |
|------|---------|
| `graph/state.py` | TypedDict for shared state across all agents |
| `graph/graph.py` | StateGraph definition, nodes, edges, entry point |
| `agents/planner.py` | Breaks query into sub-topics |
| `agents/searcher.py` | Calls Tavily API for each sub-topic |
| `agents/summarizer.py` | Summarizes search results per sub-topic |
| `agents/critic.py` | Flags contradictions across summaries |
| `agents/writer.py` | Compiles final markdown report |
| `tools/tavily_search.py` | Tavily API wrapper |
| `utils/eval.py` | Evaluation script for output quality |
| `frontend/app.py` | Streamlit UI |
| `main.py` | Entry point for CLI testing |
| `config.py` | Model names, constants, config |
| `.env` | API keys (**never commit!**) |

---

*Good luck! 🚀 The eval framework in Phase 6 is your secret weapon.*
