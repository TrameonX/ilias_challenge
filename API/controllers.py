from typing import Optional
from fastapi import APIRouter, UploadFile, File, Form, BackgroundTasks, Depends
from API.models import UploadResponse, ResultResponse, PITask, OllamaAIModel
from API.storage import JobRepository
from API.services import FileProcessingService


router = APIRouter(tags=["AI Pipeline"])

_repository = JobRepository()
_service = FileProcessingService(ai_model=OllamaAIModel(), repository=_repository)

def get_service() -> FileProcessingService:
    return _service


@router.post("/upload", response_model=UploadResponse)
async def upload_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    task: PITask = Form(PITask.SUMMARIZE),
    question: Optional[str] = Form(None),
    service: FileProcessingService = Depends(get_service),
):
    service.validate_file(file)

    job_id = service.create_job()

    file_content = await file.read()
    content_type = file.content_type

    background_tasks.add_task(
        service.process_pipeline,
        job_id=job_id,
        file_content=file_content,
        content_type=content_type,
        task=task,
        question=question,
    )

    return UploadResponse(job_id=job_id, status=service.get_job_status(job_id).status)


@router.get("/result/{job_id}", response_model=ResultResponse)
async def get_result(
    job_id: str,
    service: FileProcessingService = Depends(get_service),
):
    return service.get_job_status(job_id)
