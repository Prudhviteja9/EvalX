# ============================================================
# EvalX Dashboard - Beautiful web interface
# ============================================================
#
# Run with: streamlit run streamlit_app/dashboard.py
#
# What is Streamlit?
#   Python code that creates a web page automatically.
#   No HTML, no CSS, no JavaScript needed!
#
#   st.title("Hello")     -> Shows a big title on the page
#   st.button("Click me") -> Shows a clickable button
#   st.write(data)         -> Shows data in a table
#
# Real life:
#   FastAPI = the kitchen (processes orders behind the scenes)
#   Streamlit = the dining room (what customers see and interact with)

import sys
from pathlib import Path

# Add project root to Python path so we can import our code
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import json
import time

from app.engine import run_evaluation
from app.schemas.evaluation import EvaluationRequest, TestCase
from app.models.llm_client import SUPPORTED_MODELS


# --- PAGE CONFIGURATION ---
# Like setting up the restaurant: name, logo, layout
st.set_page_config(
    page_title="EvalX - LLM Evaluation",
    page_icon="🔬",
    layout="wide",  # Use full width of screen
)

# --- HEADER ---
st.title("EvalX")
st.subheader("LLM Evaluation & Benchmarking Framework")
st.markdown("Test and compare AI models side-by-side with real metrics.")
st.markdown("---")

# --- SIDEBAR (left panel) ---
# Like the settings panel on the left side
st.sidebar.header("Settings")

# Let user pick which models to test
available_models = list(SUPPORTED_MODELS.keys())
selected_models = st.sidebar.multiselect(
    "Select models to evaluate:",
    options=available_models,
    default=["gpt-4o-mini"],
    help="Pick one or more models to compare",
)

st.sidebar.markdown("---")
st.sidebar.markdown("**Model Pricing:**")
for model_id, info in SUPPORTED_MODELS.items():
    st.sidebar.text(f"{info['name']}: ${info['cost_per_1k_input_tokens']}/1K tokens")


# --- TABS ---
# Like different pages in a notebook
tab1, tab2, tab3 = st.tabs(["Quick Test", "Custom Test", "Results History"])


# ========== TAB 1: QUICK TEST ==========
with tab1:
    st.header("Quick Test")
    st.write("Run a pre-built 5-question test to see EvalX in action.")

    if not selected_models:
        st.warning("Please select at least one model from the sidebar.")
    else:
        if st.button("Run Quick Test", type="primary", key="quick"):
            # Create the test cases
            test_cases = [
                TestCase(question="What is the capital of Japan?", expected_answer="Tokyo", category="geography"),
                TestCase(question="What is 25 * 4?", expected_answer="100", category="math"),
                TestCase(question="Who painted the Mona Lisa?", expected_answer="Leonardo da Vinci", category="art"),
                TestCase(question="What gas do plants absorb from the atmosphere?", expected_answer="carbon dioxide", category="science"),
                TestCase(question="In what year did World War II end?", expected_answer="1945", category="history"),
            ]

            request = EvaluationRequest(
                test_cases=test_cases,
                models=selected_models,
                name="Quick Test",
            )

            # Show a spinner while running
            with st.spinner("Evaluating models... This may take a minute."):
                report = run_evaluation(request)

            st.success(f"Evaluation complete! Best model: **{report.best_model}**")
            st.session_state["last_report"] = report


# ========== TAB 2: CUSTOM TEST ==========
with tab2:
    st.header("Custom Test")
    st.write("Create your own test cases or paste JSON.")

    input_method = st.radio(
        "How do you want to input test cases?",
        ["Enter manually", "Paste JSON"],
    )

    if input_method == "Enter manually":
        st.write("Add your questions below:")
        num_questions = st.number_input("How many questions?", min_value=1, max_value=50, value=3)

        custom_test_cases = []
        for i in range(int(num_questions)):
            st.markdown(f"**Question {i+1}:**")
            col1, col2 = st.columns(2)
            with col1:
                q = st.text_input(f"Question", key=f"q_{i}", placeholder="What is 2+2?")
            with col2:
                a = st.text_input(f"Expected Answer", key=f"a_{i}", placeholder="4")
            if q and a:
                custom_test_cases.append(TestCase(question=q, expected_answer=a))

        if st.button("Run Custom Test", type="primary", key="custom"):
            if not custom_test_cases:
                st.error("Please enter at least one question and answer.")
            elif not selected_models:
                st.warning("Please select at least one model from the sidebar.")
            else:
                request = EvaluationRequest(
                    test_cases=custom_test_cases,
                    models=selected_models,
                    name="Custom Test",
                )
                with st.spinner("Evaluating..."):
                    report = run_evaluation(request)
                st.success(f"Done! Best model: **{report.best_model}**")
                st.session_state["last_report"] = report

    else:  # Paste JSON
        json_input = st.text_area(
            "Paste your test cases JSON:",
            height=200,
            placeholder='[\n  {"question": "What is 2+2?", "expected_answer": "4"},\n  {"question": "Capital of France?", "expected_answer": "Paris"}\n]',
        )

        if st.button("Run JSON Test", type="primary", key="json"):
            if not json_input:
                st.error("Please paste your JSON test cases.")
            elif not selected_models:
                st.warning("Please select at least one model from the sidebar.")
            else:
                try:
                    test_data = json.loads(json_input)
                    test_cases = [TestCase(**tc) for tc in test_data]
                    request = EvaluationRequest(
                        test_cases=test_cases,
                        models=selected_models,
                        name="JSON Test",
                    )
                    with st.spinner("Evaluating..."):
                        report = run_evaluation(request)
                    st.success(f"Done! Best model: **{report.best_model}**")
                    st.session_state["last_report"] = report
                except json.JSONDecodeError:
                    st.error("Invalid JSON! Please check your format.")


# ========== DISPLAY RESULTS ==========
# Show results if we have any (from any tab)
if "last_report" in st.session_state:
    report = st.session_state["last_report"]

    st.markdown("---")
    st.header(f"Results: {report.name}")

    # --- SUMMARY CARDS ---
    # Like the scoreboard at a sports game
    cols = st.columns(len(report.model_reports))
    for i, mr in enumerate(report.model_reports):
        with cols[i]:
            # Green border for the winner, gray for others
            is_winner = mr.model_name == report.best_model
            border_color = "#00cc66" if is_winner else "#cccccc"
            label = " (WINNER)" if is_winner else ""

            st.markdown(
                f"""
                <div style="border: 2px solid {border_color}; border-radius: 10px; padding: 15px; text-align: center;">
                    <h3>{mr.model_name}{label}</h3>
                    <h1 style="color: {border_color};">{mr.accuracy:.0%}</h1>
                    <p>Accuracy</p>
                    <p>Avg Latency: {mr.avg_latency_ms:.0f}ms</p>
                    <p>Cost: ${mr.estimated_cost:.6f}</p>
                    <p>{mr.correct_answers}/{mr.total_questions} correct</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # --- CHARTS ---
    st.markdown("---")

    # Only show comparison charts if multiple models
    if len(report.model_reports) > 1:
        st.subheader("Model Comparison")

        chart_col1, chart_col2 = st.columns(2)

        # Chart 1: Accuracy comparison (bar chart)
        with chart_col1:
            fig_accuracy = go.Figure(data=[
                go.Bar(
                    x=[mr.model_name for mr in report.model_reports],
                    y=[mr.accuracy * 100 for mr in report.model_reports],
                    marker_color=["#00cc66" if mr.model_name == report.best_model else "#4a90d9" for mr in report.model_reports],
                    text=[f"{mr.accuracy:.0%}" for mr in report.model_reports],
                    textposition="auto",
                )
            ])
            fig_accuracy.update_layout(
                title="Accuracy Comparison",
                yaxis_title="Accuracy (%)",
                yaxis_range=[0, 105],
            )
            st.plotly_chart(fig_accuracy, use_container_width=True)

        # Chart 2: Latency comparison (bar chart)
        with chart_col2:
            fig_latency = go.Figure(data=[
                go.Bar(
                    x=[mr.model_name for mr in report.model_reports],
                    y=[mr.avg_latency_ms for mr in report.model_reports],
                    marker_color=["#ff6b6b" if mr.avg_latency_ms == max(m.avg_latency_ms for m in report.model_reports) else "#4a90d9" for mr in report.model_reports],
                    text=[f"{mr.avg_latency_ms:.0f}ms" for mr in report.model_reports],
                    textposition="auto",
                )
            ])
            fig_latency.update_layout(
                title="Average Latency (lower is better)",
                yaxis_title="Latency (ms)",
            )
            st.plotly_chart(fig_latency, use_container_width=True)

        # Chart 3: Cost comparison
        chart_col3, chart_col4 = st.columns(2)

        with chart_col3:
            fig_cost = go.Figure(data=[
                go.Bar(
                    x=[mr.model_name for mr in report.model_reports],
                    y=[mr.estimated_cost * 1000 for mr in report.model_reports],
                    marker_color="#f0ad4e",
                    text=[f"${mr.estimated_cost:.6f}" for mr in report.model_reports],
                    textposition="auto",
                )
            ])
            fig_cost.update_layout(
                title="Estimated Cost",
                yaxis_title="Cost (x1000 $)",
            )
            st.plotly_chart(fig_cost, use_container_width=True)

        # Chart 4: Tokens used
        with chart_col4:
            fig_tokens = go.Figure(data=[
                go.Bar(
                    x=[mr.model_name for mr in report.model_reports],
                    y=[mr.total_tokens for mr in report.model_reports],
                    marker_color="#9b59b6",
                    text=[str(mr.total_tokens) for mr in report.model_reports],
                    textposition="auto",
                )
            ])
            fig_tokens.update_layout(
                title="Total Tokens Used",
                yaxis_title="Tokens",
            )
            st.plotly_chart(fig_tokens, use_container_width=True)

    # --- DETAILED RESULTS TABLE ---
    st.subheader("Detailed Results")

    for mr in report.model_reports:
        with st.expander(f"{mr.model_name} - {mr.accuracy:.0%} accuracy ({mr.correct_answers}/{mr.total_questions})"):
            # Convert results to a DataFrame for nice table display
            rows = []
            for r in mr.results:
                rows.append({
                    "Question": r.question[:60] + "..." if len(r.question) > 60 else r.question,
                    "Expected": r.expected_answer,
                    "Model Answer": r.model_answer[:80] + "..." if len(r.model_answer) > 80 else r.model_answer,
                    "Correct": "Yes" if r.is_correct else "No",
                    "Score": f"{r.similarity_score:.2f}",
                    "Latency": f"{r.latency_ms:.0f}ms",
                    "Tokens": r.tokens_used,
                })
            df = pd.DataFrame(rows)
            st.dataframe(df, use_container_width=True, hide_index=True)


# ========== TAB 3: RESULTS HISTORY ==========
with tab3:
    st.header("Results History")
    if "last_report" not in st.session_state:
        st.info("No results yet. Run a test first!")
    else:
        st.write("Your most recent evaluation is shown above.")
        st.write("In a production version, we would save all evaluations to a database and show history here.")


# --- FOOTER ---
st.markdown("---")
st.markdown(
    "Built by **Prudhvi Teja Yedla** | "
    "[GitHub](https://github.com/Prudhviteja9) | "
    "Powered by FastAPI + Streamlit"
)
