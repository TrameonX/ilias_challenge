from typing import Optional
from fastapi import APIRouter, UploadFile, File, Form, BackgroundTasks, Depends
from models import UploadResponse, ResultResponse, PITask, DummyAIModel, AbstractAIModel, HuggingFaceModel
from storage import JobRepository
from services import FileProcessingService
import os


router = APIRouter(tags=["AI Pipeline"])

_repository = JobRepository()


def _build_ai_model() -> AbstractAIModel:
    """
    FIX : Le modèle IA est maintenant sélectionnable via la variable d'environnement
    AI_MODEL. Remplacer le modèle ne nécessite plus de toucher au code — il suffit
    de brancher une nouvelle classe qui hérite d'AbstractAIModel et de l'enregistrer ici.
    Valeurs supportées : "dummy" (défaut). Ajouter d'autres cas selon les modèles réels.
    """
    model_name = os.getenv("AI_MODEL", "dummy").lower()
    if model_name == "dummy":
        return DummyAIModel()
    elif model_name == "huggingface":
        return HuggingFaceModel(
            api_key=os.getenv("HF_API_KEY"),
            model_id=os.getenv("HF_MODEL_ID")
        )
    raise ValueError(f"Modèle IA inconnu : '{model_name}'. Vérifiez la variable AI_MODEL.")


_service = FileProcessingService(ai_model=_build_ai_model(), repository=_repository)

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
    # FIX : le fichier est lu une seule fois ici, avant la validation.
    # Cela évite le double seek et garantit une mesure de taille fiable.
    file_content = await file.read()
    content_type = file.content_type

    service.validate_file(file, file_content)

    job_id = service.create_job()

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