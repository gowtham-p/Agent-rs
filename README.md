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

## Demo (2-min)
- 🎥 *Add a short Loom link here*
- 📸 Screenshots: `docs/images/` (answer + citations)

## Quickstart
```bash
python -m venv .venv && source .venv/bin/activate  # on Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env   # add your API key
python -c "from rag_engine import answer_question; print(answer_question('What is zero trust?'))"
