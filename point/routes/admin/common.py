from fastapi import APIRouter, UploadFile, File

from point.entity_types import PointHash
from point.services import storage

router = APIRouter(tags=["Common"])


@router.post("/upload-file")
async def upload_file(file: UploadFile = File(...)) -> PointHash:
    extension = "." + file.filename.split(".")[-1]
    file_hash = await storage.put_file(extension=extension, data=await file.read())
    return file_hash
