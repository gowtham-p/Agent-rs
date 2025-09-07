# GroundedAgent
> Production-minded RAG + Agents in Python: grounded answers with citations, evals, and guardrails.

![python](https://img.shields.io/badge/Python-3.11+-blue)
![license](https://img.shields.io/badge/license-MIT-green)
![tests](https://img.shields.io/badge/tests-passing-brightgreen)
![style](https://img.shields.io/badge/style-ruff%20%7C%20black-black)

## Why
Most “chat with your docs” demos skip the hard parts. This repo shows how to build **grounded** retrieval-augmented agents with production concerns: relevance, citations, evals, and safety.

## What
- **RAG engine** (FAISS, OpenAI embeddings) with configurable prompts
- **Citations**: return source documents & pages
- **MMR retrieval** with tunable k/fetch_k
- **Pluggable model** (`ChatOpenAI`) and prompt templates
- **Unit tests + eval hooks** for answer quality (RAGAS/DeepEval ready)
=

## Quickstart
```bash
python -m venv .venv && source .venv/bin/activate  # on Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env   # add your API key
python -c "from rag_engine import answer_question; print(answer_question('What is zero trust?'))"

## Project Structure
.
├─ src/grounded_agent/        # package (rag_engine.py lives here)
├─ data/                      # your PDFs (gitignored); include sample in examples/
├─ examples/                  # tiny sample PDFs + example notebooks
├─ tests/                     # pytest tests
├─ docs/                      # README images, architecture diagram
└─ scripts/                   # build_index.py, eval.py

## Architecture
**Flow:**
- Ingestion → Split → Embed → FAISS  
- Retriever (MMR) → Prompt ({question}, {context}) → LLM  
- Citations returned alongside answers


## Configuration

- `TEXT_SPLIT_CHUNK_SIZE`, `CHUNK_OVERLAP`, `K`, `FETCH_K`  
  via **env** or `.yaml`  

- `MODEL` and `EMBEDDING_MODEL`  
  set in **.env**

