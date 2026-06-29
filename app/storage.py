import os
import uuid
from typing import Dict, Optional
from datetime import datetime, timezone

from fastapi import HTTPException
from API.models import JobStatus, ResultResponse, StoredDocument

# ---------------------------------------------------------------------------
# Lazy MongoDB client — importé seulement si motor est disponible.
# Cela permet de faire tourner les tests unitaires sans MongoDB.
# ---------------------------------------------------------------------------
def _get_mongo_client():
    """Retourne un AsyncIOMotorClient configuré via MONGO_URL."""
    try:
        from motor.motor_asyncio import AsyncIOMotorClient
        mongo_url = os.getenv("MONGO_URL", "mongodb://localhost:27017")
        return AsyncIOMotorClient(mongo_url)
    except ImportError:
        return None


# ---------------------------------------------------------------------------
# JobRepository — stockage en mémoire des statuts de jobs (inchangé)
# En production : remplacer le dict par une collection MongoDB ici.
# ---------------------------------------------------------------------------
class JobRepository:
    """
    Couche Storage des statuts de jobs.
    Intentionnellement séparée du stockage des fichiers (principe SRP).
    """

    def __init__(self):
        self._store: Dict[str, ResultResponse] = {}

    def create(self, job_id: str) -> ResultResponse:
        job = ResultResponse(job_id=job_id, status=JobStatus.PENDING)
        self._store[job_id] = job
        return job

    def get(self, job_id: str) -> ResultResponse:
        if job_id not in self._store:
            raise HTTPException(status_code=404, detail="Identifiant de tâche introuvable.")
        return self._store[job_id]

    def set_running(self, job_id: str):
        self._store[job_id].status = JobStatus.RUNNING

    def set_completed(self, job_id: str, result: dict):
        self._store[job_id].status = JobStatus.COMPLETED
        self._store[job_id].result = result

    def set_failed(self, job_id: str, error: str):
        self._store[job_id].status = JobStatus.FAILED
        self._store[job_id].error = error


# ---------------------------------------------------------------------------
# DocumentRepository — persistance des fichiers bruts dans MongoDB / GridFS
# ---------------------------------------------------------------------------
class DocumentRepository:
    """
    Stocke les fichiers uploadés (txt, pdf) dans MongoDB :
      - Binaire du fichier  → GridFS  (collection fs.files / fs.chunks)
      - Métadonnées du doc  → collection « documents »

    Usage :
        repo = DocumentRepository()
        doc = await repo.save(job_id, filename, content_type, raw_bytes)
        doc = await repo.get_by_job(job_id)
        raw = await repo.get_file_bytes(doc.gridfs_id)
    """

    DB_NAME = "ai_platform"
    COLLECTION = "documents"

    def __init__(self):
        self._client = _get_mongo_client()

    @property
    def _db(self):
        if self._client is None:
            raise RuntimeError(
                "motor n'est pas installé ou MONGO_URL est inaccessible. "
                "Ajoutez `motor>=3.3` dans requirements.txt."
            )
        return self._client[self.DB_NAME]

    @property
    def _collection(self):
        return self._db[self.COLLECTION]

    async def save(
        self,
        job_id: str,
        filename: str,
        content_type: str,
        raw_bytes: bytes,
    ) -> StoredDocument:
        """Persiste le fichier binaire dans GridFS et les méta dans 'documents'."""
        import gridfs
        from motor.motor_asyncio import AsyncIOMotorGridFSBucket

        bucket = AsyncIOMotorGridFSBucket(self._db)
        gridfs_id = await bucket.upload_from_stream(
            filename,
            raw_bytes,
            metadata={
                "job_id": job_id,
                "content_type": content_type,
                "uploaded_at": datetime.now(timezone.utc).isoformat(),
            },
        )

        document_id = str(uuid.uuid4())
        doc = StoredDocument(
            document_id=document_id,
            job_id=job_id,
            filename=filename,
            content_type=content_type,
            size_bytes=len(raw_bytes),
            gridfs_id=str(gridfs_id),
        )

        await self._collection.insert_one(
            {
                **doc.model_dump(),
                "created_at": datetime.now(timezone.utc),
            }
        )
        return doc

    async def get_by_job(self, job_id: str) -> Optional[StoredDocument]:
        """Récupère les métadonnées du document associé à un job_id."""
        record = await self._collection.find_one({"job_id": job_id})
        if not record:
            return None
        record.pop("_id", None)
        record.pop("created_at", None)
        return StoredDocument(**record)

    async def get_file_bytes(self, gridfs_id: str) -> bytes:
        """Télécharge le binaire depuis GridFS à partir de son ObjectId."""
        from bson import ObjectId
        from motor.motor_asyncio import AsyncIOMotorGridFSBucket

        bucket = AsyncIOMotorGridFSBucket(self._db)
        stream = await bucket.open_download_stream(ObjectId(gridfs_id))
        return await stream.read()

    async def list_all(self, limit: int = 100) -> list[StoredDocument]:
        """Liste les derniers documents persistés (utile pour un dashboard)."""
        cursor = self._collection.find({}).sort("created_at", -1).limit(limit)
        docs = []
        async for record in cursor:
            record.pop("_id", None)
            record.pop("created_at", None)
            docs.append(StoredDocument(**record))
        return docs