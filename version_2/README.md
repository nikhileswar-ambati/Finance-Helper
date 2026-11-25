# Finance Helper — Version 2

Finance Helper turns one project brief into evidence-linked financial software requirements, review findings, SDLC guidance, and an IEEE 830-1998 SRS Word document. This version has no interview flow: submit the brief once. Supporting documents are optional.

## Setup and run (PowerShell)

Run these commands from the project folder:

```powershell
cd C:\Users\nikhi\OneDrive\Desktop\PROJECTS\SE\version_2
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
Copy-Item .env.example .env
notepad .env
```

In `.env`, add your Groq API key to `GROQ_API_KEY=` and save the file. The project brief and retrieved source excerpts are sent to Groq for requirement generation when the key is configured. Without a key, the app creates evidence-only draft requirements locally. Keep `.env` private.

Start the app:

```powershell
py -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8001
```

Open <http://127.0.0.1:8001>. API documentation is at <http://127.0.0.1:8001/docs>. Stop the server with **Ctrl+C**.

## Workflow

1. Enter one project brief and optionally attach source files.
2. The Requirements Agent retrieves evidence, drafts requirements, and runs quality and compliance checks.
3. Finance Helper selects an SDLC recommendation from the brief and requirements.
4. The separate SRS Generation Agent creates a Word document using the brief, requirements, and SDLC decision.
5. Review the results in the existing left-sidebar sections and use **Download SRS**.

The generated requirements and SRS remain drafts until reviewed by a person. The SRS uses IEEE 830-1998 sections and retains requirement evidence traceability.

## Agents

- **Requirements Agent** — gathers and classifies requirements from the single brief and retrieved source evidence, then records quality and compliance findings.
- **SRS Generation Agent** — independently composes the IEEE 830-1998 Word document from the saved project baseline.
- **Governance & SDLC Agent** — provides the SDLC advisory shown in the existing workflow.

Project records, ChromaDB vectors, and generated exports are stored under `data/` in this version_2 folder.
