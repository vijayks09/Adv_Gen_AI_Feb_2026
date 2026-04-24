# RAG Customer Support Assistant

## Features
- PDF-based question answering
- ChromaDB vector storage
- LangGraph workflow (2-node)
- Human-in-the-loop (HITL) escalation

## Flow
PDF → Chunk → Embedding → ChromaDB  
Query → Retrieve → LLM → Output / Escalation

## Run
```bash
pip install -r requirements.txt
python main.py