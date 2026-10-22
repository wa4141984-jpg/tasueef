"""AI Study Assistant - Business & Marketing.  Run with:  streamlit run app.py"""
import sys
from pathlib import Path

# Make sure Python can find the helper files that sit next to this app.py,
# no matter which folder the host (e.g. Streamlit Cloud) starts the app from.
APP_DIR = Path(__file__).resolve().parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

import streamlit as st

# set_page_config must be the first Streamlit command.
st.set_page_config(page_title="AI Study Assistant", page_icon="📈", layout="centered",
                   initial_sidebar_state="expanded")

# ---------- startup checks: give a clear message instead of a crash ----------
REQUIRED_FILES = ["ai_service.py", "app_config.py", "file_processing.py",
                  "input_checks.py", "prompts.py", "styles.py", "requirements.txt"]
missing_files = [f for f in REQUIRED_FILES if not (APP_DIR / f).exists()]
if missing_files:
    st.error("Some project files are missing, so the app cannot start.")
    st.markdown("Upload these files to the **same folder as `app.py`** in your "
                "GitHub repository, then reboot the app:")
    st.code("\n".join(missing_files))
    st.stop()

try:
    import ai_service
    import app_config as config
    import file_processing
    import input_checks as validators
    import prompts
    from styles import CSS
except ModuleNotFoundError as e:
    st.error(f"A required Python package is missing: {e.name}")
    st.markdown("Make sure `requirements.txt` is in your repository and lists "
                "`streamlit`, `anthropic`, `python-dotenv`, `pypdf`, and `python-docx`, "
                "then reboot the app.")
    st.stop()

st.markdown(CSS, unsafe_allow_html=True)

# ---------- session state ----------
st.session_state.setdefault("messages", [])   # {"role", "content" (sent to AI), "display"}
st.session_state.setdefault("pending", False)  # True when an answer must be generated


def reset_session():
    st.session_state.messages = []
    st.session_state.pending = False


# ---------- header ----------
st.markdown(
    f"""<div class="hero"><h1>{config.APP_NAME}</h1>
    <p>Ask about marketing or business topics, or upload your notes and case studies.
    Get explanations, analyses, quizzes, and flashcards at your level.</p></div>""",
    unsafe_allow_html=True,
)

# ---------- API key check ----------
api_key = config.get_api_key()
if not api_key:
    st.error("No API key found. The app cannot contact the AI yet.")
    st.markdown(
        "**Fix it in 2 steps:**\n"
        "1. Copy `.env.example` to `.env` and set `ANTHROPIC_API_KEY=your key`\n"
        "   (on Streamlit Cloud, add it under *App settings → Secrets*).\n"
        "2. Restart the app.\n\nSee the README for how to get a key."
    )
    st.stop()

# ---------- sidebar ----------
with st.sidebar:
    st.subheader("Study settings")
    mode = st.selectbox("What do you need?", list(prompts.MODES.keys()))
    level = st.radio("Difficulty", list(prompts.LEVELS.keys()), index=1)
    length = st.radio("Answer length", list(prompts.LENGTHS.keys()), index=1, horizontal=True)
    st.divider()
    if st.button("Start a new session", use_container_width=True):
        reset_session()
        st.rerun()
    st.markdown(
        '<p class="note">AI can make mistakes and has no live internet access. '
        "Verify important facts, figures, and citations before using them in "
        "assignments.</p>", unsafe_allow_html=True)

# ---------- input form ----------
with st.form("study_form", clear_on_submit=False):
    question = st.text_area(
        "Your topic or question",
        height=150,
        max_chars=config.MAX_QUESTION_CHARS,
        placeholder="e.g. Explain market segmentation using Nike as an example, "
                    "or paste a case study to analyze.",
    )
    files = st.file_uploader(
        f"Upload notes or readings (optional, up to {config.MAX_FILES} files, "
        f"{config.MAX_FILE_MB} MB each)",
        type=config.ALLOWED_EXTENSIONS,
        accept_multiple_files=True,
        help="Supported: PDF, Word (.docx), text, Markdown, CSV. Scanned PDFs are not supported.",
    )
    submitted = st.form_submit_button("Generate", type="primary")

if submitted:
    errors = validators.validate_question(question) + validators.validate_files(files)
    if errors:
        for e in errors:
            st.error(e)
    else:
        try:
            with st.spinner("Reading your files..."):
                documents, warnings = file_processing.process_files(files)
            for w in warnings:
                st.warning(w)
            first = prompts.build_first_message(mode, level, length, question.strip(), documents)
            shown = f"**{mode}** · {level}\n\n{question.strip()}"
            if documents:
                shown += "\n\n📎 " + ", ".join(name for name, _ in documents)
            st.session_state.messages = [{"role": "user", "content": first, "display": shown}]
            st.session_state.pending = True
        except file_processing.FileReadError as e:
            st.error(str(e))

# ---------- follow-up input ----------
if st.session_state.messages and not st.session_state.pending:
    follow_up = st.chat_input("Ask a follow-up question...")
    if follow_up:
        problems = validators.validate_question(follow_up)
        if len(st.session_state.messages) >= config.MAX_MESSAGES_PER_SESSION:
            st.warning("This session is full. Start a new session from the sidebar.")
        elif problems:
            st.error(problems[0])
        else:
            st.session_state.messages.append(
                {"role": "user", "content": follow_up.strip(), "display": follow_up.strip()})
            st.session_state.pending = True

# ---------- show conversation ----------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["display"])

# ---------- generate answer ----------
if st.session_state.pending:
    st.session_state.pending = False
    api_messages = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
    with st.chat_message("assistant"):
        try:
            client = ai_service.create_client(api_key)
            with st.spinner("Thinking..."):
                stream = ai_service.stream_answer(client, config.get_model(),
                                                  prompts.SYSTEM_PROMPT, api_messages)
                answer = st.write_stream(stream)
            st.session_state.messages.append(
                {"role": "assistant", "content": answer, "display": answer})
            st.rerun()  # redraw so the follow-up box appears
        except ai_service.AIServiceError as e:
            st.error(str(e))
            st.session_state.messages.pop()  # drop the unanswered question so you can retry
        except Exception:
            st.error("Something unexpected went wrong. Please try again.")
            st.session_state.messages.pop()

# ---------- download ----------
if any(m["role"] == "assistant" for m in st.session_state.messages):
    export = "\n\n---\n\n".join(
        f"**{'You' if m['role'] == 'user' else 'Assistant'}:**\n\n{m['display']}"
        for m in st.session_state.messages)
    st.download_button("Download study notes (.md)", export,
                       file_name="study_notes.md", mime="text/markdown")
