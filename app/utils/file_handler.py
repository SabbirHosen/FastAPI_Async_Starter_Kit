import os
import uuid
from fastapi import UploadFile
import aiofiles

async def save_upload_file(upload_file: UploadFile, destination_dir: str) -> str:
    os.makedirs(destination_dir, exist_ok=True)
    filename = f"{uuid.uuid4()}_{upload_file.filename}"
    file_path = os.path.join(destination_dir, filename)
    async with aiofiles.open(file_path, 'wb') as out_file:
        content = await upload_file.read()
        await out_file.write(content)
    return file_path
