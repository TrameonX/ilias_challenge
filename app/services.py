import uuid
import asyncio
import io
from typing import Optional
from fastapi import HTTPException, UploadFile
from API.models import JobStatus, ResultResponse, AbstractAIModel, PITask
from API.storage import JobRepository, DocumentRepository


class FileProcessingService:

    def __init__(self, ai_model: AbstractAIModel, repository: JobRepository):
        self.ai_model = ai_model
        self.repository = repository
        self.doc_repository = DocumentRepository()

    def validate_file(self, file: UploadFile):
        allowed_extensions = ["txt", "pdf"]
        allowed_content_types = ["text/plain", "application/pdf"]

        file_ext = file.filename.split(".")[-1].lower() if file.filename else ""

        if file_ext not in allowed_extensions or file.content_type not in allowed_content_types:
            raise HTTPException(
                status_code=400,
                detail="Format non supporté. Seuls les fichiers .txt et .pdf sont acceptés."
            )

        MAX_FILE_SIZE = 5 * 1024 * 1024
        file.file.seek(0, 2)
        file_size = file.file.tell()
        file.file.seek(0)

        if file_size > MAX_FILE_SIZE:
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
        filename: str = "upload",
        question: Optional[str] = None,
    ):
        try:
            self.repository.set_running(job_id)

            # ----------------------------------------------------------------
            # 1. Persistance MongoDB : on stocke le fichier brut AVANT tout
            #    traitement IA. Ainsi le document est toujours récupérable,
            #    même si l'inférence échoue par la suite.
            # ----------------------------------------------------------------
            try:
                await self.doc_repository.save(
                    job_id=job_id,
                    filename=filename,
                    content_type=content_type,
                    raw_bytes=file_content,
                )
            except Exception as mongo_err:
                # On logue l'erreur MongoDB mais on ne bloque PAS le pipeline :
                # le traitement IA peut continuer même sans persistance.
                print(f"[WARN] Impossible de persister le document en MongoDB : {mongo_err}")

            # ----------------------------------------------------------------
            # 2. Extraction du texte
            # ----------------------------------------------------------------
            if content_type == "application/pdf" or file_content[:4] == b"%PDF":
                text_content = self._extract_pdf(file_content)
            else:
                text_content = file_content.decode("utf-8", errors="replace")

            await asyncio.sleep(1)

            # ----------------------------------------------------------------
            # 3. Inférence IA
            # ----------------------------------------------------------------
            await asyncio.sleep(2)
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