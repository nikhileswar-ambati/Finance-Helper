"""ZIP-added interview, governance, evaluation, and SRS API endpoints."""
from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, JSONResponse

from app.schemas import InterviewQuestionRequest, InterviewQuestionResponse
from app.services.compliance import catalogue as rbi_catalogue
from app.services.llm import enabled as llm_enabled, select_interview_question
from app.services.storage import ProjectStore

router = APIRouter()
store = ProjectStore()
ROOT = Path(__file__).resolve().parent
INTERVIEW_TOPICS = [
    {"key": "workflow and outcomes", "topic": "Workflow and outcomes"},
    {"key": "business rules", "topic": "Decision rules"},
    {"key": "exceptions", "topic": "Exceptions and overrides"},
    {"key": "data and integrations", "topic": "Data and integrations"},
    {"key": "security and compliance", "topic": "Security and compliance"},
    {"key": "service levels and scale", "topic": "Operational scale"},
    {"key": "delivery constraints", "topic": "Delivery context"},
    {"key": "validation and rollout", "topic": "Validation and rollout"},
]


def _project(project_id: str):
    try:
        return store.get(project_id)
    except KeyError as exc:
        raise HTTPException(404, "Project not found.") from exc


@router.get("/api/knowledge-base/rbi")
def rbi_knowledge_base() -> JSONResponse:
    return JSONResponse({
        "jurisdiction": "India",
        "authority": "Reserve Bank of India",
        "sources": rbi_catalogue(),
        "notice": "Source applicability and legal interpretation require authorised compliance review.",
    })


@router.post("/api/interview/next-question", response_model=InterviewQuestionResponse)
def next_interview_question(request: InterviewQuestionRequest) -> InterviewQuestionResponse:
    asked = set(request.asked_question_keys)
    candidates = [item for item in INTERVIEW_TOPICS if item["key"] not in asked]
    if not candidates:
        return InterviewQuestionResponse(mode="Local fallback", completed=True)
    answers = {key: value.strip()[:4000] for key, value in request.answers.items() if value.strip()}
    if llm_enabled():
        try:
            return InterviewQuestionResponse(**select_interview_question(request.functionality.strip(), answers, candidates), mode="Groq adaptive agent")
        except RuntimeError as exc:
            raise HTTPException(503, str(exc)) from exc
    topic = candidates[0]
    return InterviewQuestionResponse(
        **topic,
        prompt=f"To complete the project picture, describe the {topic['topic'].lower()} for this solution.",
        mode="Local fallback",
    )


@router.post("/api/projects/{project_id}/srs")
def generate_srs(project_id: str) -> JSONResponse:
    project = _project(project_id)
    if not project.requirements:
        raise HTTPException(422, "Generate requirements before creating the SRS.")
    output_dir = store.root / "exports" / project.id
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "ieee-830-1998-srs.docx"
    from app.services.srs import create_ieee_830_document
    output_path.write_bytes(create_ieee_830_document(project))
    return JSONResponse({"download_url": f"/api/projects/{project.id}/srs/download"})


@router.get("/api/projects/{project_id}/srs/download")
def download_srs(project_id: str) -> FileResponse:
    project = _project(project_id)
    path = store.root / "exports" / project.id / "ieee-830-1998-srs.docx"
    if not path.is_file():
        raise HTTPException(404, "Generate the SRS before downloading it.")
    return FileResponse(path, filename=f"srs-{project.id}.docx", media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document")


@router.get("/api/projects/{project_id}/artefacts")
def get_artefacts(project_id: str) -> JSONResponse:
    project = _project(project_id)
    return JSONResponse(project.artefacts)


@router.get("/api/projects/{project_id}/evaluation")
def get_evaluation(project_id: str) -> JSONResponse:
    project = _project(project_id)
    if project.evaluation is None:
        raise HTTPException(404, "Generate requirements before retrieving evaluation metrics.")
    return JSONResponse(project.evaluation.model_dump(mode="json"))


@router.get("/api/projects/{project_id}/agent-runs")
def get_agent_runs(project_id: str) -> JSONResponse:
    return JSONResponse([item.model_dump(mode="json") for item in _project(project_id).agent_runs])
