# ============================================================
# GRADER = Checks if the LLM's answer is correct
# ============================================================
#
# Real life:
#   Teacher has answer key: "Paris"
#   Student wrote: "The capital of France is Paris."
#   Teacher checks: Does the student's answer CONTAIN "Paris"? YES → Correct!
#
# We use TWO methods to grade:
#   1. Containment check: Does the answer contain the expected answer?
#   2. Similarity score: How similar are the two texts? (0.0 to 1.0)


def check_answer(expected: str, actual: str) -> dict:
    """
    Grade an LLM's answer against the expected answer.

    Parameters:
        expected: The correct answer (from our test dataset)
        actual:   What the LLM actually said

    Returns:
        {
            "is_correct": True/False,
            "similarity_score": 0.0 to 1.0,
            "method": which grading method was used
        }

    Examples:
        check_answer("Paris", "Paris.")
        → { is_correct: True, similarity_score: 1.0 }

        check_answer("Paris", "The capital of France is Paris")
        → { is_correct: True, similarity_score: 0.85 }

        check_answer("Paris", "London")
        → { is_correct: False, similarity_score: 0.0 }
    """

    # Clean both answers (remove extra spaces, make lowercase)
    # Like the teacher ignoring capitalization when grading
    expected_clean = expected.strip().lower()
    actual_clean = actual.strip().lower()

    # METHOD 1: Exact match (after cleaning)
    # "paris" == "paris" → True
    if expected_clean == actual_clean:
        return {
            "is_correct": True,
            "similarity_score": 1.0,
            "method": "exact_match",
        }

    # METHOD 2: Containment check
    # Does "the capital of france is paris" CONTAIN "paris"? → YES
    if expected_clean in actual_clean:
        # Calculate how much of the answer is the expected part
        # If expected = "Paris" (5 chars) and actual = "The capital is Paris" (20 chars)
        # similarity = 5/20 = 0.25... but we know it's correct, so boost it
        similarity = max(0.8, len(expected_clean) / max(len(actual_clean), 1))
        return {
            "is_correct": True,
            "similarity_score": round(similarity, 3),
            "method": "containment",
        }

    # METHOD 3: Word overlap
    # Split both into words and see how many words match
    # expected: {"paris"}
    # actual: {"the", "capital", "is", "berlin"} → "paris" not found → wrong
    expected_words = set(expected_clean.split())
    actual_words = set(actual_clean.split())

    # How many expected words appear in the actual answer?
    if len(expected_words) > 0:
        matching_words = expected_words.intersection(actual_words)
        overlap = len(matching_words) / len(expected_words)
    else:
        overlap = 0.0

    # If more than 60% of expected words are in the answer → consider correct
    is_correct = overlap >= 0.6

    return {
        "is_correct": is_correct,
        "similarity_score": round(overlap, 3),
        "method": "word_overlap",
    }


def estimate_cost(tokens_used: int, model_name: str) -> float:
    """
    Estimate how much money this API call cost.

    Real life:
        Like checking your restaurant bill.
        Different dishes (models) cost different amounts.
        More food (tokens) = higher bill.

    Parameters:
        tokens_used: How many tokens were used
        model_name:  Which model was used

    Returns:
        Estimated cost in US dollars
    """

    # Price per 1000 tokens (approximate, combined input+output)
    prices = {
        "gpt-4o-mini": 0.0004,       # Very cheap
        "gpt-4o": 0.006,             # Expensive but smart
        "gpt-3.5-turbo": 0.001,      # Cheap
    }

    price_per_1k = prices.get(model_name, 0.001)  # Default price if model unknown
    cost = (tokens_used / 1000) * price_per_1k

    return round(cost, 6)
