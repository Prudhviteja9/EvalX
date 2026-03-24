# ============================================================
# ENGINE = The brain of EvalX
# ============================================================
#
# This connects everything:
#   Test Cases → LLM Client → Grader → Report
#
# Real life analogy:
#   You're a SCHOOL PRINCIPAL running an exam:
#   1. You have the exam papers (test cases)
#   2. You give them to each student (LLM models)
#   3. You collect answers and grade them (grader)
#   4. You write a report card for each student (report)
#   5. You pick the best student (best model)

from app.models.llm_client import LLMClient
from app.evaluators.grader import check_answer, estimate_cost
from app.schemas.evaluation import (
    TestCase,
    EvaluationRequest,
    SingleResult,
    ModelReport,
    EvaluationReport,
)


def run_evaluation(request: EvaluationRequest) -> EvaluationReport:
    """
    Run a complete evaluation.

    This is the MAIN function that does everything:
      1. Takes test cases + list of models
      2. Sends each question to each model
      3. Grades every answer
      4. Creates a report comparing all models

    Parameters:
        request: Contains test_cases and models to test

    Returns:
        EvaluationReport with results for all models

    Real life:
        run_evaluation(
            test_cases = [10 geography questions],
            models = ["gpt-4o-mini", "gpt-3.5-turbo"]
        )
        → Report showing which model got more answers right
    """

    # Create our LLM client (the messenger who talks to AI models)
    client = LLMClient()

    # This will hold the report for each model
    all_model_reports = []

    # --- LOOP THROUGH EACH MODEL ---
    # Like giving the same exam to each student, one by one
    for model_name in request.models:
        print(f"\n--- Testing model: {model_name} ---")

        model_results = []       # Results for this model
        total_tokens = 0         # Total tokens this model used
        total_latency = 0        # Total time this model took
        correct_count = 0        # How many it got right

        # --- LOOP THROUGH EACH TEST CASE ---
        # Like each question on the exam
        for i, test_case in enumerate(request.test_cases):
            print(f"  Question {i+1}/{len(request.test_cases)}: {test_case.question[:50]}...")

            try:
                # STEP 1: Ask the model the question
                llm_response = client.ask_model(
                    model_name=model_name,
                    question=test_case.question,
                    context=test_case.context,
                )

                # STEP 2: Grade the answer
                grade = check_answer(
                    expected=test_case.expected_answer,
                    actual=llm_response["answer"],
                )

                # STEP 3: Create a result for this question
                result = SingleResult(
                    question=test_case.question,
                    expected_answer=test_case.expected_answer,
                    model_answer=llm_response["answer"],
                    is_correct=grade["is_correct"],
                    similarity_score=grade["similarity_score"],
                    latency_ms=llm_response["latency_ms"],
                    tokens_used=llm_response["tokens_used"],
                )

                model_results.append(result)

                # Update totals
                total_tokens += llm_response["tokens_used"]
                total_latency += llm_response["latency_ms"]
                if grade["is_correct"]:
                    correct_count += 1

                status = "CORRECT" if grade["is_correct"] else "WRONG"
                print(f"    -> {status} (score: {grade['similarity_score']})")

            except Exception as e:
                # If something goes wrong (API error, timeout, etc.)
                # Don't crash - record the error and continue
                print(f"    -> ERROR: {str(e)}")
                result = SingleResult(
                    question=test_case.question,
                    expected_answer=test_case.expected_answer,
                    model_answer=f"ERROR: {str(e)}",
                    is_correct=False,
                    similarity_score=0.0,
                    latency_ms=0,
                    tokens_used=0,
                )
                model_results.append(result)

        # --- CREATE REPORT FOR THIS MODEL ---
        total_questions = len(request.test_cases)
        accuracy = correct_count / total_questions if total_questions > 0 else 0
        avg_latency = total_latency / total_questions if total_questions > 0 else 0

        model_report = ModelReport(
            model_name=model_name,
            total_questions=total_questions,
            correct_answers=correct_count,
            accuracy=round(accuracy, 3),
            avg_latency_ms=round(avg_latency, 2),
            total_tokens=total_tokens,
            estimated_cost=estimate_cost(total_tokens, model_name),
            results=model_results,
        )

        all_model_reports.append(model_report)
        print(f"\n  {model_name} RESULTS: {correct_count}/{total_questions} correct ({accuracy:.0%})")

    # --- FIND THE BEST MODEL ---
    # The model with the highest accuracy wins
    # Like finding the student with the highest exam score
    best_model = max(all_model_reports, key=lambda r: r.accuracy)

    # --- CREATE THE FINAL REPORT ---
    report = EvaluationReport(
        name=request.name,
        model_reports=all_model_reports,
        best_model=best_model.model_name,
        total_test_cases=len(request.test_cases),
    )

    print(f"\n{'='*50}")
    print(f"WINNER: {best_model.model_name} with {best_model.accuracy:.0%} accuracy!")
    print(f"{'='*50}")

    return report
