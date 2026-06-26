import uuid
import asyncio
import io
from typing import Optional
from fastapi import HTTPException, UploadFile
from models import JobStatus, ResultResponse, AbstractAIModel, PITask
from storage import JobRepository


class FileProcessingService:

    def __init__(self, ai_model: AbstractAIModel, repository: JobRepository):
        self.ai_model = ai_model
        self.repository = repository

    def validate_file(self, file: UploadFile, file_content: bytes):
        """
        FIX : La validation reçoit maintenant les bytes déjà lus pour mesurer
        la taille de manière fiable. L'approche seek/tell sur un fichier streamé
        pouvait retourner 0 et laisser passer des fichiers trop lourds.
        """
        allowed_extensions = ["txt", "pdf"]
        allowed_content_types = ["text/plain", "application/pdf"]

        file_ext = file.filename.split(".")[-1].lower() if file.filename else ""

        if file_ext not in allowed_extensions or file.content_type not in allowed_content_types:
            raise HTTPException(
                status_code=400,
                detail="Format non supporté. Seuls les fichiers .txt et .pdf sont acceptés."
            )

        MAX_FILE_SIZE = 5 * 1024 * 1024
        if len(file_content) > MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail="Le fichier dépasse la taille maximale de 5 Mo.")

    def create_job(self) -> str:
        job_id = str(uuid.uuid4())
        self.repository.create(job_id)
        return job_id

    async def process_pipeline(
        self,
        job_id: str,
        file_content: bytes,
        content_type: str,
        task: PITask,
        question: Optional[str] = None,
    ):
        try:
            self.repository.set_running(job_id)

            if content_type == "application/pdf" or file_content[:4] == b"%PDF":
                text_content = self._extract_pdf(file_content)
            else:
                text_content = file_content.decode("utf-8", errors="replace")

            # FIX : les deux asyncio.sleep() redondants ont été fusionnés en un seul.
            # Ils simulaient artificiellement un délai de traitement sans raison documentée.
            await asyncio.sleep(1)

            ai_insights = self.ai_model.run_inference(task, text_content, question)

            self.repository.set_completed(job_id, ai_insights)

        except Exception as e:
            self.repository.set_failed(job_id, f"Erreur durant le traitement : {str(e)}")

    def _extract_pdf(self, file_content: bytes) -> str:
        try:
            from pypdf import PdfReader
            reader = PdfReader(io.BytesIO(file_content))
            pages = [page.extract_text() or "" for page in reader.pages]
            text = "\n\n".join(pages).strip()
            return text if text else "[PDF sans texte extractible — document scanné ou protégé.]"
        except Exception as e:
            return f"[Erreur extraction PDF : {str(e)}]"

    def get_job_status(self, job_id: str) -> ResultResponse:
        return self.repository.get(job_id)