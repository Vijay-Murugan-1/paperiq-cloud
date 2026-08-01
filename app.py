import streamlit as st
import boto3
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

# --- CONFIGURATION ---
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME", "")
API_ENDPOINT = os.getenv("QUERY_API_URL", "")

st.set_page_config(page_title="PaperIQ!", page_icon="📚", layout="wide")

# ==========================================
# 1. INITIALIZE SESSION STATE MEMORY
# ==========================================
if "paper" not in st.session_state:
    st.session_state.paper = None

if "results_cache" not in st.session_state:
    st.session_state.results_cache = {}


def parse_response_payload(raw_data):
    """
    Safely converts strings, markdown codeblocks, or dictionaries into clean Python data structures.
    """
    if isinstance(raw_data, (dict, list)):
        return raw_data

    if isinstance(raw_data, str):
        cleaned = raw_data.replace("```json", "").replace("```", "").strip()
        try:
            return json.loads(cleaned)
        except Exception:
            return raw_data

    return raw_data


# Helper function to call your AWS Lambda API
def query_aws_assistant(task: str, doc_id: str, question: str = None, extra_params: dict = None):
    payload = {
        "task": task,
        "document_id": doc_id,
    }
    if question:
        payload["question"] = question
    if extra_params:
        payload.update(extra_params)

    response = requests.post(
        API_ENDPOINT,
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    return response


# ==========================================
# 2. MAIN APPLICATION
# ==========================================
def main() -> None:
    st.title("PaperIQ! 📚")
    st.subheader("AI-based research assistant for papers (AWS Cloud Powered)")

    st.write(
        "PaperIQ helps you quickly understand academic papers using serverless AI. "
        "Upload a PDF to Amazon S3, and ask questions, generate summaries, key insights, quizzes, or flashcards."
    )

    if not S3_BUCKET_NAME or not API_ENDPOINT:
        st.warning("⚠️ `.env` variables missing! Ensure `S3_BUCKET_NAME` and `QUERY_API_URL` are set in `.env`.")

    # --- FILE UPLOADER & S3 INGESTION ---
    uploaded_file = st.file_uploader("Upload a paper", type=["pdf"])

    if uploaded_file is not None:
        file_name = uploaded_file.name
        st.info(f"Selected file: **{file_name}**")

        if st.session_state.paper is None or st.session_state.paper["name"] != file_name:
            if st.button("🚀 Process & Upload Paper to Cloud", type="primary"):
                with st.spinner("Uploading to AWS S3..."):
                    try:
                        s3_client = boto3.client("s3")
                        s3_client.upload_fileobj(uploaded_file, S3_BUCKET_NAME, file_name)

                        st.session_state.paper = {
                            "name": file_name,
                            "s3_bucket": S3_BUCKET_NAME
                        }
                        st.session_state.results_cache = {}
                        st.success(f"Uploaded `{file_name}`! Ingestion triggered in AWS.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to upload to S3: {e}")

    # --- FEATURE SELECTION (ONCE PAPER IS ACTIVE) ---
    if st.session_state.paper is not None:
        doc_id = st.session_state.paper["name"]
        st.success(f"Active Document: `{doc_id}`")
        st.divider()

        feature = st.radio(
            "Choose a feature",
            ("Summary", "Ask Questions", "Key Insights", "Quiz Generator", "Flashcards"),
            horizontal=True
        )

        # ------------------------------------------
        # FEATURE 1: SUMMARY
        # ------------------------------------------
        if feature == "Summary":
            if st.button("Generate Summary"):
                with st.spinner("Generating summary via Gemini & AWS..."):
                    res = query_aws_assistant(task="summary", doc_id=doc_id)
                    if res.status_code == 200:
                        data = res.json()
                        st.session_state.results_cache["summary"] = data.get("result", data.get("response"))
                    else:
                        st.error(f"Error {res.status_code}: {res.text}")

            if "summary" in st.session_state.results_cache:
                st.subheader("Paper Summary")
                st.write(st.session_state.results_cache["summary"])

        # ------------------------------------------
        # FEATURE 2: ASK QUESTIONS (QA)
        # ------------------------------------------
        elif feature == "Ask Questions":
            user_query = st.text_input("Ask a question about the paper")

            if st.button("Submit Question") and user_query:
                with st.spinner("Searching Pinecone vectors & generating answer..."):
                    res = query_aws_assistant(task="qa", doc_id=doc_id, question=user_query)
                    if res.status_code == 200:
                        data = res.json()
                        st.session_state.results_cache["qa_answer"] = data.get("result", data.get("response"))
                    elif res.status_code == 404:
                        st.warning("No vector index found yet. Please wait a few seconds for S3 Lambda processing.")
                    else:
                        st.error(f"Error {res.status_code}: {res.text}")

            if "qa_answer" in st.session_state.results_cache:
                st.subheader("Answer")
                st.write(st.session_state.results_cache["qa_answer"])

        # ------------------------------------------
        # FEATURE 3: KEY INSIGHTS
        # ------------------------------------------
        elif feature == "Key Insights":
            if st.button("Generate Insights"):
                with st.spinner("Extracting key insights..."):
                    res = query_aws_assistant(task="insights", doc_id=doc_id)
                    if res.status_code == 200:
                        data = res.json()
                        raw_result = data.get("result", data.get("response"))
                        parsed = parse_response_payload(raw_result)

                        # Standardize into a list of insights
                        if isinstance(parsed, dict) and "insights" in parsed:
                            st.session_state.results_cache["insights"] = parsed["insights"]
                        elif isinstance(parsed, list):
                            st.session_state.results_cache["insights"] = parsed
                        else:
                            st.session_state.results_cache["insights"] = parsed
                    else:
                        st.error(f"Error {res.status_code}: {res.text}")

            if "insights" in st.session_state.results_cache:
                st.subheader("Key Insights")
                insights = st.session_state.results_cache["insights"]

                if isinstance(insights, list):
                    for item in insights:
                        with st.container(border=True):
                            if isinstance(item, dict):
                                st.markdown(f"### 💡 {item.get('title', 'Insight')}")
                                st.write(item.get('description', ''))
                            else:
                                st.write(str(item))
                else:
                    st.write(insights)

        # ------------------------------------------
        # FEATURE 4: QUIZ GENERATOR
        # ------------------------------------------
        elif feature == "Quiz Generator":
            num_q = st.slider("Number of questions", min_value=3, max_value=10, value=5)

            if st.button("Generate Quiz"):
                with st.spinner("Generating quiz..."):
                    res = query_aws_assistant(task="quiz", doc_id=doc_id, extra_params={"num_questions": num_q})
                    if res.status_code == 200:
                        data = res.json()
                        raw_result = data.get("result", data.get("response"))
                        parsed = parse_response_payload(raw_result)

                        # Extract questions list
                        if isinstance(parsed, dict) and "quiz" in parsed:
                            quiz_list = parsed["quiz"]
                        elif isinstance(parsed, dict) and "questions" in parsed:
                            quiz_list = parsed["questions"]
                        elif isinstance(parsed, list):
                            quiz_list = parsed
                        else:
                            quiz_list = None

                        if quiz_list:
                            st.session_state.quiz_data = quiz_list
                            st.session_state.show_results = False
                            st.session_state.user_answers = {}
                        else:
                            st.warning("Could not parse quiz questions structure.")
                            st.write(raw_result)
                    else:
                        st.error(f"Error {res.status_code}: {res.text}")

            if "quiz_data" in st.session_state:
                st.subheader("Test Your Knowledge")
                with st.form("quiz_form"):
                    user_answers = {}
                    for i, q in enumerate(st.session_state.quiz_data):
                        st.write(f"**Q{i+1}: {q.get('question', '')}**")
                        user_answers[i] = st.radio(
                            "Options", 
                            q.get("options", []), 
                            key=f"q_{i}", 
                            label_visibility="collapsed", 
                            index=None
                        )
                        st.write("---")

                    submitted = st.form_submit_button("Submit Answers")
                    if submitted:
                        st.session_state.user_answers = user_answers
                        st.session_state.show_results = True

                if st.session_state.get("show_results"):
                    score = 0
                    for i, q in enumerate(st.session_state.quiz_data):
                        user_ans = st.session_state.user_answers.get(i)
                        correct_ans = q.get("correct_answer") or q.get("answer")

                        if user_ans == correct_ans:
                            score += 1
                            st.success(f"**Q{i+1} Correct!**\n\n{q.get('explanation', '')}")
                        else:
                            st.error(f"**Q{i+1} Incorrect.**\n\n**You chose:** {user_ans}\n\n**Correct answer:** {correct_ans}\n\n*Explanation: {q.get('explanation', '')}*")

                    st.write(f"### Final Score: {score} / {len(st.session_state.quiz_data)}")

        # ------------------------------------------
        # FEATURE 5: FLASHCARDS
        # ------------------------------------------
        elif feature == "Flashcards":
            num_cards = st.slider("Number of Flashcards", min_value=5, max_value=20, value=10)

            if st.button("Generate Flashcards"):
                with st.spinner("Extracting flashcards..."):
                    res = query_aws_assistant(task="flashcards", doc_id=doc_id, extra_params={"num_cards": num_cards})
                    if res.status_code == 200:
                        data = res.json()
                        raw_result = data.get("result", data.get("response"))
                        parsed = parse_response_payload(raw_result)

                        # Extract flashcards list
                        if isinstance(parsed, dict) and "flashcards" in parsed:
                            cards_list = parsed["flashcards"]
                        elif isinstance(parsed, dict) and "cards" in parsed:
                            cards_list = parsed["cards"]
                        elif isinstance(parsed, list):
                            cards_list = parsed
                        else:
                            cards_list = None

                        if cards_list:
                            st.session_state.flashcards_data = cards_list
                            st.session_state.current_card = 0
                            st.session_state.is_flipped = False
                        else:
                            st.warning("Could not parse flashcard structure.")
                            st.write(raw_result)
                    else:
                        st.error(f"Error {res.status_code}: {res.text}")

            if "flashcards_data" in st.session_state:
                cards = st.session_state.flashcards_data
                idx = st.session_state.current_card

                st.markdown(f"### Card {idx + 1} of {len(cards)}")
                current_card_data = cards[idx]

                front = current_card_data.get("front") or current_card_data.get("question") or current_card_data.get("concept")
                back = current_card_data.get("back") or current_card_data.get("answer") or current_card_data.get("definition")

                if not st.session_state.is_flipped:
                    st.info(f"**Front (Concept / Question):**\n\n### {front}")
                else:
                    st.success(f"**Back (Definition / Answer):**\n\n{back}")

                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button("⬅️ Previous", disabled=(idx == 0)):
                        st.session_state.current_card -= 1
                        st.session_state.is_flipped = False
                        st.rerun()
                with col2:
                    if st.button("🔄 Flip Card"):
                        st.session_state.is_flipped = not st.session_state.is_flipped
                        st.rerun()
                with col3:
                    if st.button("Next ➡️", disabled=(idx == len(cards) - 1)):
                        st.session_state.current_card += 1
                        st.session_state.is_flipped = False
                        st.rerun()

if __name__ == "__main__":
    main()