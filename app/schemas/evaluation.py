# ============================================================
# SCHEMAS = The "forms" that define what our data looks like
# ============================================================
#
# Real life analogy:
#   Hospital form has: Name (text), Age (number), Phone (number)
#   If you put "hello" in Age field → ERROR! Age must be a number.
#
#   Same here: We define EXACTLY what fields each data has,
#   and what TYPE each field must be (text, number, list, etc.)
#
# We use Pydantic (a library) to create these "forms"
#   - It auto-validates data (catches wrong types)
#   - It auto-generates documentation
#   - It's used by FastAPI to know what data to expect

from pydantic import BaseModel
from typing import Optional


# ----- 1. TEST CASE -----
# One question to ask the LLM
#
# Example:
#   {
#     "question": "What is the capital of France?",
#     "expected_answer": "Paris",
#     "context": "France is a country in Western Europe.",
#     "category": "geography"
#   }

class TestCase(BaseModel):
    question: str                          # The question to ask the LLM
    expected_answer: str                   # The correct answer (to compare against)
    context: Optional[str] = None          # Extra info the LLM can use (optional)
    category: Optional[str] = "general"    # Category like "geography", "math" (optional)


# ----- 2. EVALUATION REQUEST -----
# What the user sends to our API
# "Here are my test cases, test them on these models"
#
# Example:
#   {
#     "test_cases": [... list of test cases ...],
#     "models": ["gpt-4o-mini", "gpt-3.5-turbo"],
#     "name": "My Geography Test"
#   }

class EvaluationRequest(BaseModel):
    test_cases: list[TestCase]             # List of questions to test
    models: list[str] = ["gpt-4o-mini"]    # Which LLMs to test (default: gpt-4o-mini)
    name: str = "Untitled Evaluation"      # Name for this test run


# ----- 3. SINGLE RESULT -----
# The result of ONE question answered by ONE model
#
# Example:
#   {
#     "question": "What is the capital of France?",
#     "expected_answer": "Paris",
#     "model_answer": "The capital of France is Paris.",
#     "is_correct": true,
#     "similarity_score": 0.95,
#     "latency_ms": 230,
#     "tokens_used": 45
#   }

class SingleResult(BaseModel):
    question: str                          # The question that was asked
    expected_answer: str                   # What the answer SHOULD be
    model_answer: str                      # What the LLM actually said
    is_correct: bool                       # Did it get it right? True/False
    similarity_score: float                # How similar (0.0 = different, 1.0 = identical)
    latency_ms: float                      # How long it took in milliseconds
    tokens_used: int                       # How many tokens (words) it used


# ----- 4. MODEL REPORT -----
# Summary of how ONE model did on ALL questions
#
# Example:
#   {
#     "model_name": "gpt-4o-mini",
#     "total_questions": 10,
#     "correct_answers": 8,
#     "accuracy": 0.80,
#     "avg_latency_ms": 245.5,
#     "total_tokens": 450,
#     "estimated_cost": 0.0023,
#     "results": [... list of individual results ...]
#   }

class ModelReport(BaseModel):
    model_name: str                        # Which model (e.g., "gpt-4o-mini")
    total_questions: int                   # How many questions were asked
    correct_answers: int                   # How many it got right
    accuracy: float                        # Percentage correct (0.0 to 1.0)
    avg_latency_ms: float                  # Average response time
    total_tokens: int                      # Total tokens used
    estimated_cost: float                  # Estimated cost in dollars
    results: list[SingleResult]            # Individual results for each question


# ----- 5. FULL EVALUATION REPORT -----
# The complete report comparing ALL models
#
# Example:
#   {
#     "name": "My Geography Test",
#     "model_reports": [
#       { model_name: "gpt-4o-mini", accuracy: 0.80, ... },
#       { model_name: "gpt-3.5-turbo", accuracy: 0.70, ... }
#     ],
#     "best_model": "gpt-4o-mini",
#     "total_test_cases": 10
#   }

class EvaluationReport(BaseModel):
    name: str                              # Name of this evaluation
    model_reports: list[ModelReport]       # Results for each model
    best_model: str                        # Which model won (highest accuracy)
    total_test_cases: int                  # How many questions were tested
