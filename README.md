# EvalX - LLM Evaluation & Benchmarking Framework

Test and compare AI models (GPT-4, Claude, Llama) side-by-side with real metrics: accuracy, hallucination detection, latency, and cost.

## Live Demo

[Live Dashboard](https://evalx-llm.streamlit.app) | [GitHub Repo](https://github.com/Prudhviteja9/EvalX)

## Architecture

```
User (Browser/API)
      |
      v
  FastAPI Server (REST API)
      |
      |--- /evaluate     --> Evaluation Engine
      |--- /benchmark    --> Sample Dataset (10 questions)
      |--- /quick-test   --> Demo (5 questions)
      |--- /evaluate/pdf --> PDF Report Generator
      |
      v
  Evaluation Engine
      |
      |--- LLM Client (sends questions to AI models)
      |       |--- OpenAI (GPT-4o, GPT-4o-mini, GPT-3.5)
      |       |--- Anthropic (Claude) [planned]
      |       |--- Hugging Face (open-source models) [planned]
      |
      |--- Grader (checks if answers are correct)
      |       |--- Exact match
      |       |--- Containment check
      |       |--- Word overlap scoring
      |
      v
  Report Generator
      |--- JSON response (API)
      |--- PDF report (downloadable)
      |--- Streamlit Dashboard (interactive charts)
```

## Features

- **Multi-model evaluation** - Test GPT-4o, GPT-4o-mini, GPT-3.5-turbo side-by-side
- **Automated grading** - Smart answer checking (exact match, containment, word overlap)
- **Performance metrics** - Accuracy, latency (ms), token usage, cost estimation
- **Interactive dashboard** - Streamlit UI with Plotly charts for visual comparison
- **PDF reports** - Generate professional evaluation reports
- **REST API** - FastAPI with auto-generated docs at `/docs`
- **Custom test cases** - Upload your own questions or use built-in benchmarks
- **Docker support** - Containerized for easy deployment

## Tech Stack

| Category | Technology |
|----------|-----------|
| Backend | Python, FastAPI |
| LLM APIs | OpenAI API (GPT-4o, GPT-4o-mini, GPT-3.5) |
| Evaluation | Custom grading engine (3 methods) |
| Dashboard | Streamlit, Plotly |
| Reports | fpdf2 (PDF generation) |
| Data | Pandas |
| DevOps | Docker, docker-compose |
| Testing | Pytest |

## Quick Start

### 1. Clone and install

```bash
git clone https://github.com/Prudhviteja9/EvalX.git
cd EvalX
pip install -r requirements.txt
```

### 2. Set up API key

```bash
# Create .env file
echo "OPENAI_API_KEY=your_key_here" > .env
```

### 3. Run the API

```bash
uvicorn app.main:app --reload --port 8000
# Visit http://localhost:8000/docs
```

### 4. Run the Dashboard

```bash
streamlit run streamlit_app/dashboard.py
# Visit http://localhost:8501
```

### 5. Or use Docker

```bash
docker compose up
# API: http://localhost:8000
# Dashboard: http://localhost:8501
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Welcome page |
| GET | `/health` | Health check |
| GET | `/models` | List supported models |
| POST | `/evaluate` | Run custom evaluation |
| GET | `/quick-test` | 5-question demo |
| GET | `/benchmark` | 10-question benchmark |
| POST | `/evaluate/pdf` | Evaluate + download PDF report |

## Sample Results

```
Model: gpt-4o-mini
  Accuracy:    100%
  Avg Latency: 1139ms
  Total Tokens: 216
  Est. Cost:   $0.000086

Model: gpt-3.5-turbo
  Accuracy:    80%
  Avg Latency: 856ms
  Total Tokens: 198
  Est. Cost:   $0.000198
```

## Project Structure

```
EvalX/
├── app/
│   ├── main.py              # FastAPI endpoints
│   ├── engine.py             # Evaluation orchestrator
│   ├── models/
│   │   └── llm_client.py     # LLM API connections
│   ├── evaluators/
│   │   └── grader.py         # Answer grading logic
│   ├── schemas/
│   │   └── evaluation.py     # Data models (Pydantic)
│   └── utils/
│       └── pdf_report.py     # PDF report generator
├── streamlit_app/
│   └── dashboard.py          # Interactive dashboard
├── data/
│   └── sample_test.json      # Benchmark dataset
├── Dockerfile                # Container config
├── docker-compose.yml        # Multi-container setup
├── requirements.txt          # Dependencies
└── README.md
```

## What I Learned

- Designed a modular evaluation pipeline separating LLM clients, graders, and report generators
- Implemented three grading strategies (exact match, containment, word overlap) to handle varied LLM response formats
- Built both API (FastAPI) and UI (Streamlit) interfaces for different user workflows
- Managed cost estimation and latency tracking across multiple LLM providers

## License

MIT

---

Built by [Prudhvi Teja Yedla](https://github.com/Prudhviteja9)
