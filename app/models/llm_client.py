# ============================================================
# LLM CLIENT = Talks to AI models (GPT, Claude, etc.)
# ============================================================
#
# Real life analogy:
#   You're a teacher giving exams.
#   You walk to Student's room → give question → start timer
#   → student answers → you collect answer + stop timer
#
#   This file does the SAME THING but with AI models:
#   Connect to GPT → send question → start timer
#   → GPT answers → collect answer + stop timer + count tokens

import os
import time
from dotenv import load_dotenv
from openai import OpenAI

# Load API keys from .env file
# Like opening your wallet to get your credit card
load_dotenv()


class LLMClient:
    """
    Talks to LLM models and gets their answers.

    Think of this class as a MESSENGER:
      You give it a question → it goes to GPT → brings back the answer
    """

    def __init__(self):
        """
        Set up the connection to OpenAI.
        Like dialing a phone number before you can talk.
        """
        # Check Streamlit secrets first, then environment variable
        api_key = os.getenv("OPENAI_API_KEY")

        # Also check Streamlit secrets (for cloud deployment)
        if not api_key:
            try:
                import streamlit as st
                api_key = st.secrets.get("OPENAI_API_KEY")
            except Exception:
                pass

        if not api_key:
            raise ValueError(
                "No OpenAI API key found! "
                "Enter your key in the sidebar or set OPENAI_API_KEY in .env"
            )

        # Create the OpenAI client (our "phone connection" to GPT)
        self.openai_client = OpenAI(api_key=api_key)

    def ask_model(self, model_name: str, question: str, context: str = None) -> dict:
        """
        Ask a model a question and get the answer.

        Parameters:
            model_name: Which model to ask (e.g., "gpt-4o-mini")
            question:   The question to ask
            context:    Extra information to help answer (optional)

        Returns:
            A dictionary with:
              - answer: What the model said
              - latency_ms: How long it took (milliseconds)
              - tokens_used: How many tokens it used

        Real life:
            ask_model("gpt-4o-mini", "What is the capital of France?")
            → { answer: "Paris", latency_ms: 230, tokens_used: 15 }
        """

        # Build the message to send
        # "messages" is how you talk to ChatGPT via API
        # system = instructions for the AI (like telling a student "answer briefly")
        # user = the actual question
        messages = [
            {
                "role": "system",
                "content": "You are a helpful assistant. Answer questions accurately and concisely.",
            },
        ]

        # If we have context (extra info), add it to the question
        if context:
            user_message = f"Context: {context}\n\nQuestion: {question}"
        else:
            user_message = question

        messages.append({"role": "user", "content": user_message})

        # START THE TIMER (like pressing start on a stopwatch)
        start_time = time.time()

        # SEND THE QUESTION TO THE MODEL
        # This is where the actual API call happens
        # Like the messenger running to GPT's room and asking the question
        response = self.openai_client.chat.completions.create(
            model=model_name,
            messages=messages,
            temperature=0,  # 0 = always give the same answer (consistent for testing)
        )

        # STOP THE TIMER
        end_time = time.time()
        latency_ms = (end_time - start_time) * 1000  # Convert seconds to milliseconds

        # EXTRACT THE ANSWER from the response
        # The response object has a specific structure:
        #   response.choices[0].message.content = the actual text answer
        answer = response.choices[0].message.content

        # COUNT TOKENS USED
        # Tokens = small pieces of words (like syllables)
        # We pay per token, so we track this
        tokens_used = response.usage.total_tokens

        # RETURN everything as a dictionary
        return {
            "answer": answer,
            "latency_ms": round(latency_ms, 2),
            "tokens_used": tokens_used,
        }


# ============================================================
# SUPPORTED MODELS
# ============================================================
# These are the models we can test with.
# Each has different speed, accuracy, and cost.
#
# Think of them like different "students" taking the exam:
#   gpt-4o-mini  = Fast and cheap student (good enough for most tasks)
#   gpt-4o       = Smart but expensive student (best answers)
#   gpt-3.5-turbo = Old but very fast student (cheapest)

SUPPORTED_MODELS = {
    "gpt-4o-mini": {
        "name": "GPT-4o Mini",
        "cost_per_1k_input_tokens": 0.00015,
        "cost_per_1k_output_tokens": 0.0006,
    },
    "gpt-4o": {
        "name": "GPT-4o",
        "cost_per_1k_input_tokens": 0.0025,
        "cost_per_1k_output_tokens": 0.01,
    },
    "gpt-3.5-turbo": {
        "name": "GPT-3.5 Turbo",
        "cost_per_1k_input_tokens": 0.0005,
        "cost_per_1k_output_tokens": 0.0015,
    },
}
