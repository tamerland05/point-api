from fastapi import APIRouter, UploadFile, File

from point.entity_types import PointHash
from point.services import storage

router = APIRouter(tags=["Common"])


@router.post("/upload-file")
async def upload_file(file: UploadFile = File(...)) -> PointHash:
    file_hash = await storage.put_file(filename=file.filename, data=await file.read())
    return file_hash
