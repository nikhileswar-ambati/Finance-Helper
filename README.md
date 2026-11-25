# Finance Helper

Finance Helper is a local, finance-only requirements workspace. It collects stakeholder context, indexes project sources, retrieves evidence for requirement drafts, checks quality, and prepares delivery and governance material for human review.

## Features

- Finance-only project intake with a stakeholder interview and financial source uploads (TXT, Markdown, CSV, PDF, DOCX).
- Sensitive identifier masking before indexing, ChromaDB project collections, local embeddings, and optional OpenAI-compatible LLM support.
- Evidence-linked requirement drafts with editing, approval, clarification requests, and deterministic quality checks.
- RBI reference summaries, reviewable control suggestions, risk register, and source-to-requirement traceability.
- Agent run history, audit and approval records, evaluation metrics, and derived requirements artefacts.
- Context-aware SDLC recommendations with human approval gates.
- IEEE 830-1998 SRS export to Word (`.docx`) and Markdown requirements pack export.

RBI applicability suggestions are advisory and require authorised compliance or legal review. This prototype has no authentication or multi-user isolation.

## Setup and run (Windows PowerShell)

Use 64-bit Python 3.13. Run these commands from the project directory. Recreate the virtual environment with `--clear` so compiled packages cannot be carried over from a different Python version.

```powershell
# 1. If the app is running, stop it with Ctrl+C. Deactivate only if a venv is active:
if ($env:VIRTUAL_ENV) { deactivate }

# 2. Create or rebuild the Python 3.13 virtual environment
py -3.13 -m venv --clear .venv

# 3. Activate it
.\.venv\Scripts\Activate.ps1

# If PowerShell blocks activation, allow it for this terminal only and activate again:
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1

# 4. Install dependencies
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

# 5. Confirm the compiled Pydantic extension and application import correctly
python -c "import pydantic_core._pydantic_core; import app.main; print('Imports OK')"

# 6. Create local configuration (skip if .env already exists)
if (-not (Test-Path .env)) { Copy-Item .env.example .env }

# 7. Start the web app
python -m uvicorn app.main:app --reload
```

Open the workspace at <http://127.0.0.1:8000> and the API docs at <http://127.0.0.1:8000/docs>. Stop the server with `Ctrl+C`.

### Repair an existing environment

If startup reports `No module named 'pydantic_core._pydantic_core'`, the virtual environment contains a compiled wheel for a different Python version. The most reliable fix is to stop the server, deactivate the environment, then rerun the setup commands above. To repair the currently activated environment without clearing it, reinstall every requirement for its active Python interpreter:

```powershell
python -m pip install --force-reinstall --no-cache-dir -r requirements.txt
python -c "import pydantic_core._pydantic_core; import app.main; print('Imports OK')"
```

A plain `pip install -r requirements.txt` can leave the incompatible binary in place when pip thinks the package version is already satisfied.

The app uses Groq for requirements generation and adaptive stakeholder interviews. Create a Groq API key, then add it to `.env`:

```dotenv
GROQ_API_KEY=your-groq-api-key
LLM_BASE_URL=https://api.groq.com/openai/v1
LLM_MODEL=openai/gpt-oss-20b
```

After each interview response, Finance Helper sends the project workflow, previous question-and-answer transcript, and unanswered topic list to Groq to choose and write the next follow-up. Without `GROQ_API_KEY`, the app uses local fallback questions. Keep `.env` private and never commit API keys.

Embeddings use the separate optional `EMBEDDING_API_KEY` and `EMBEDDING_BASE_URL` settings. For OpenAI embeddings, set `OPENAI_API_KEY`; otherwise the app uses local embeddings. The existing `EMBEDDING_MODEL` setting selects the model used by that embeddings provider.

## Other useful commands

```powershell
# Check service health while the server is running
Invoke-RestMethod http://127.0.0.1:8000/api/health

# Run automated tests
python -m pytest -q

# Leave the virtual environment
deactivate
```

For Command Prompt, activate with `.venv\Scripts\activate.bat`. On macOS/Linux, create the environment with `python3 -m venv .venv`, activate with `source .venv/bin/activate`, install with `python -m pip install -r requirements.txt`, then run `python -m uvicorn app.main:app --reload`.

## Added API endpoints

- `GET /api/knowledge-base/rbi` — list the RBI reference pack and applicability notice.
- `POST /api/interview/next-question` — choose the next unanswered interview topic, using a configured LLM or local fallback.
- `GET /api/projects/{project_id}/agent-runs` — view the staged analysis run history.
- `GET /api/projects/{project_id}/artefacts` — retrieve SRS, user stories, use cases, traceability, risk, and compliance artefacts as JSON.
- `GET /api/projects/{project_id}/evaluation` — retrieve citation, acceptance, control, issue, and human-review metrics.
- `POST /api/projects/{project_id}/srs` — generate the IEEE 830-1998 Word document.
- `GET /api/projects/{project_id}/srs/download` — download the generated SRS.

Existing routes cover project intake, source retrieval, requirements, edits, approval, clarifications, SDLC review, and JSON/Markdown export. Browse `/docs` for the full interactive API reference.

## Project layout

- `app/main.py` and `app/features.py`: finance intake and feature API routes.
- `app/services/`: document handling, RAG, requirement generation, compliance, risk, evaluation, artefacts, agents, SRS, SDLC, and storage.
- `app/prompts/`: requirement and interview prompt templates.
- `app/templates/` and `app/static/`: Finance Helper interface.
- `sample_data/`: example source material.
- `tests/`: automated tests.
- `data/`: local JSON project records, ChromaDB index, and generated SRS files.
