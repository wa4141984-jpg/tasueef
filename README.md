# AI Study Assistant (Business & Marketing)

A beginner-friendly Streamlit app that helps students study business and marketing.
Type a question or upload notes/readings, and the AI will explain concepts, analyze
case studies, draft marketing plans, run SWOT/PESTEL analyses, summarize material,
write quizzes, and make flashcards. You can ask follow-up questions and download
your notes.

## Features
- Seven study modes, three difficulty levels, three answer lengths
- Upload up to 3 files (PDF, DOCX, TXT, MD, CSV), 5 MB each
- Answers stream in live, with loading indicators
- Input validation and plain-language error messages
- API key kept in environment variables or Streamlit secrets (never in code)
- Responsive layout that works on phones

## Project structure
```
ai-study-assistant/
├── app.py                  # Streamlit interface (start here)
├── ai_service.py           # Talks to the AI API, handles API errors
├── prompts.py              # Study modes and instructions sent to the AI
├── file_processing.py      # Extracts text from uploaded files
├── input_checks.py         # Checks text and file inputs
├── app_config.py           # Settings, limits, and API key loading
├── styles.py               # Custom CSS
├── requirements.txt
├── .env.example            # Template for your key (no real secrets)
├── .gitignore              # Keeps .env out of Git
└── .streamlit/
    ├── config.toml         # Theme and upload limit
    └── secrets.toml.example
```

## 1. Get an API key
This app uses the Anthropic (Claude) API.
1. Go to https://console.anthropic.com and create an account.
2. Open **Billing** and add a small amount of credit (API use is pay-as-you-go).
3. Open **API Keys → Create Key**, name it, and copy it. It is shown only once.

Treat the key like a password: never paste it into code, screenshots, or GitHub.

## 2. Install
You need Python 3.10 or newer.

```bash
cd ai-study-assistant
python -m venv venv

# Activate the virtual environment
source venv/bin/activate        # macOS / Linux
venv\Scripts\activate           # Windows

pip install -r requirements.txt
```

## 3. Configure the key
```bash
cp .env.example .env            # Windows: copy .env.example .env
```
Open `.env` and replace `your-api-key-here` with your real key:
```
ANTHROPIC_API_KEY=sk-ant-...
```
Alternatively, copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml`
and put the key there. Both files are listed in `.gitignore`.

Optional: set `ANTHROPIC_MODEL` to use a different Claude model. Check the
current model names at https://docs.claude.com.

## 4. Run locally
```bash
streamlit run app.py
```
Your browser opens at http://localhost:8501.

## 5. Deploy (Streamlit Community Cloud, free)
1. Push the project to a **GitHub** repository. Confirm `.env` and
   `secrets.toml` are NOT in the repo (`.gitignore` handles this).
2. Go to https://share.streamlit.io and sign in with GitHub.
3. Click **Create app**, choose your repository, branch, and set the main file to `app.py`.
4. Open **Advanced settings → Secrets** and paste:
   ```toml
   ANTHROPIC_API_KEY = "your real key"
   ```
5. Click **Deploy**. You get a public URL in a few minutes.

Other hosts (Render, Railway, Hugging Face Spaces) also work: set
`ANTHROPIC_API_KEY` as an environment variable and use the start command
`streamlit run app.py --server.port $PORT --server.address 0.0.0.0`.

**Before deploying, check your GitHub repo.** It must contain all of these files
in the same folder as `app.py`: `ai_service.py`, `app_config.py`,
`file_processing.py`, `input_checks.py`, `prompts.py`, `styles.py`, and
`requirements.txt`. (Upload the files themselves, not the zip.) The app shows a list
of any missing files if you forget one.

**Cost warning:** anyone with your public URL spends your API credit. Set a
monthly spend limit in the Anthropic Console, or make the app private.

## Troubleshooting
| Message | What to do |
|---|---|
| `ModuleNotFoundError: No module named 'ai_service'` or "project files are missing" | Some files were not uploaded to GitHub. Every `.py` file and `requirements.txt` must sit in the same folder as `app.py` (see the checklist above), then reboot the app |
| "No API key found" | Check `.env` is in the project folder and restart the app |
| "Your API key was rejected" | Re-copy the key; make sure there are no spaces or quotes |
| "No credit left" | Add credit under Billing in the Console |
| "model was not found" | Fix or remove `ANTHROPIC_MODEL` |
| "No readable text found" | The file is probably a scan or image; use a text-based file |

## Limitations
- **AI can be wrong.** It may produce errors or outdated facts. Verify figures,
  dates, and citations before using them in graded work.
- **No internet access.** It cannot look up current news, prices, or company data.
- **Scanned PDFs and images are not read** (no OCR). Tables in PDFs may extract poorly.
- **Size limits:** about 60,000 characters of file text per request (longer
  files are trimmed), and CSVs are cut to the first 200 rows.
- **Short sessions:** a session holds up to 20 messages to control costs.
  History is lost when you refresh the page; use the download button to keep notes.
- **No user accounts or rate limiting.** If you deploy publicly, add
  authentication (for example `st.login`) and spending limits.
- **Not professional advice.** Not a substitute for your instructor, textbook,
  or for legal, tax, or investment advice.
- Do not upload confidential or personal data: file contents are sent to the
  AI provider.
- Not tested against the live API here, so run it once locally with your own key
  to confirm your setup.
