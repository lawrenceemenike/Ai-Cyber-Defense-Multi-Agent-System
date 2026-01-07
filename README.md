# AI Cyber-Defense Multi-Agent System (CADMS)

## Overview
Autonomous threat detection and mitigation planning via 12-step LangGraph pipeline.

## Project Structure
- `src/graph/graph.py`: LangGraph orchestration logic (12-step pipeline).
- `src/main.py`: FastAPI entry point.
- `src/agents/`: Agent logic implementations.
- `docker-compose.yml`: Infrastructure (Postgres, Redis, ChromaDB).

## Getting Started

### Prerequisites
- Python 3.10+
- Docker & Docker Compose

### Setup
1. Install dependencies:
   ```bash
   pip install poetry
   poetry install
   ```
2. Start infrastructure:
   ```bash
   docker-compose up -d
   ```
3. Run API:
   ```bash
   poetry run python src/main.py
   ```

### Usage
Send a POST request to `http://localhost:8000/ingest`:
```json
{
  "source": "firewall",
  "event_type": "traffic",
  "timestamp": "2024-01-01T12:00:00Z",
  "raw_payload": {"src_ip": "1.2.3.4", "dest_port": 22}
}
```
