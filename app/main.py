# ============================================================
# EvalX - LLM Evaluation & Benchmarking Framework
# main.py = The FRONT DOOR of our app (all API endpoints)
# ============================================================

import json
import os
from pathlib import Path
from fastapi import FastAPI, Query
from fastapi.responses import FileResponse
from app.schemas.evaluation import (
    EvaluationRequest,
    EvaluationReport,
    TestCase,
)
from app.engine import run_evaluation
from app.models.llm_client import SUPPORTED_MODELS
from app.utils.pdf_report import generate_pdf_report


# --- CREATE THE APP ---
app = FastAPI(
    title="EvalX",
    description="LLM Evaluation & Benchmarking Framework - Test and compare AI models",
    version="1.0.0",
)


# --- ENDPOINT 1: HOME ---
# GET = "give me information" (like reading a menu)
# URL: http://localhost:8000/

@app.get("/")
def home():
    """Welcome page - shows app info."""
    return {
        "app": "EvalX",
        "status": "running",
        "message": "Welcome to EvalX! Your LLM Evaluation Framework is ready.",
        "docs": "Visit /docs to see all available endpoints",
    }


# --- ENDPOINT 2: HEALTH CHECK ---
# URL: http://localhost:8000/health

@app.get("/health")
def health_check():
    """Check if the app is alive."""
    return {"status": "healthy"}


# --- ENDPOINT 3: LIST SUPPORTED MODELS ---
# URL: http://localhost:8000/models
#
# Real life: Like asking a restaurant "what dishes do you have?"
# Returns the list of AI models we can test.

@app.get("/models")
def list_models():
    """Show all LLM models available for testing."""
    return {
        "supported_models": SUPPORTED_MODELS,
        "total": len(SUPPORTED_MODELS),
    }


# --- ENDPOINT 4: RUN EVALUATION ---
# POST = "here's data, do something with it" (like placing an order)
# URL: http://localhost:8000/evaluate
#
# This is the MAIN endpoint - the whole reason EvalX exists!
#
# Real life:
#   Customer gives waiter their order (test cases + models)
#   Waiter takes it to kitchen (engine processes it)
#   Waiter brings back the food (evaluation report)
#
# POST vs GET:
#   GET  = "give me something" (reading)  - no data sent
#   POST = "here's data, process it" (writing) - data sent in body

@app.post("/evaluate", response_model=EvaluationReport)
def evaluate(request: EvaluationRequest):
    """
    Run an evaluation on one or more LLM models.

    Send test cases and model names, get back a full report
    with accuracy, latency, cost, and per-question results.
    """
    report = run_evaluation(request)
    return report


# --- ENDPOINT 5: QUICK TEST ---
# URL: http://localhost:8000/quick-test
#
# A simple endpoint with pre-built test cases
# So users can try EvalX immediately without creating their own test data
# Like a "free sample" at a restaurant

@app.get("/quick-test")
def quick_test():
    """
    Run a quick demo evaluation with 5 sample questions.
    No setup needed - just hit this endpoint to see EvalX in action!
    """
    sample_test_cases = [
        TestCase(
            question="What is the capital of Japan?",
            expected_answer="Tokyo",
            category="geography",
        ),
        TestCase(
            question="What is 25 * 4?",
            expected_answer="100",
            category="math",
        ),
        TestCase(
            question="Who painted the Mona Lisa?",
            expected_answer="Leonardo da Vinci",
            category="art",
        ),
        TestCase(
            question="What gas do plants absorb from the atmosphere?",
            expected_answer="carbon dioxide",
            category="science",
        ),
        TestCase(
            question="In what year did World War II end?",
            expected_answer="1945",
            category="history",
        ),
    ]

    request = EvaluationRequest(
        test_cases=sample_test_cases,
        models=["gpt-4o-mini"],
        name="Quick Demo Test",
    )

    report = run_evaluation(request)
    return report


# --- ENDPOINT 6: RUN BENCHMARK (from sample file) ---
# URL: http://localhost:8000/benchmark?models=gpt-4o-mini&models=gpt-3.5-turbo
#
# Loads the 10-question benchmark from data/sample_test.json
# and runs it on the models you choose.
#
# Real life: Like a STANDARDIZED TEST (SAT/GRE)
# Same questions for everyone, compare fairly.

@app.get("/benchmark")
def run_benchmark(
    models: list[str] = Query(default=["gpt-4o-mini"]),
):
    """
    Run the 10-question general knowledge benchmark.
    Pass ?models=gpt-4o-mini&models=gpt-3.5-turbo to compare models.
    """
    data_path = Path(__file__).parent.parent / "data" / "sample_test.json"
    with open(data_path, "r") as f:
        data = json.load(f)

    test_cases = [TestCase(**tc) for tc in data["test_cases"]]

    request = EvaluationRequest(
        test_cases=test_cases,
        models=models,
        name=data["name"],
    )

    report = run_evaluation(request)
    return report


# --- ENDPOINT 7: EVALUATE + DOWNLOAD PDF ---
# POST: http://localhost:8000/evaluate/pdf
#
# Same as /evaluate but also generates a PDF report
# and returns it as a downloadable file.
#
# Real life: Like getting your exam results PRINTED on paper.

@app.post("/evaluate/pdf")
def evaluate_and_download_pdf(request: EvaluationRequest):
    """
    Run evaluation and download results as a PDF report.
    """
    report = run_evaluation(request)

    # Create reports folder if it doesn't exist
    reports_dir = Path(__file__).parent.parent / "reports"
    reports_dir.mkdir(exist_ok=True)

    # Generate PDF
    pdf_path = str(reports_dir / f"evalx_report_{report.name.replace(' ', '_')}.pdf")
    generate_pdf_report(report, pdf_path)

    return FileResponse(
        path=pdf_path,
        filename=f"EvalX_Report_{report.name.replace(' ', '_')}.pdf",
        media_type="application/pdf",
    )
