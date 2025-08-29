from fastapi import FastAPI , APIRouter , Depends, UploadFile, File , status
from fastapi.responses import JSONResponse
import os
from helpers.config import Settings, get_settings
from controllers import DataController , ProjectController
from models.enums import ResponseSignal
import aiofiles
import logging

logger = logging.getLogger('uvicorn.error')
data_routes = APIRouter(
    prefix="/api/v1/data",
    tags=["data","rag"]
)
@data_routes.post("/upload/{project_id}")

async def upload_file(project_id:str ,file:UploadFile, 
                    app_settings: Settings = Depends(get_settings)):
    data_controller = DataController()
    
    is_validate , response =data_controller.validate_uploaded_file(file = file)
    if(not is_validate):
        return {
            "status": status.HTTP_400_BAD_REQUEST,
            "signal": response
    
        }
    
    project_dir_path = ProjectController().get_project_path(project_id=project_id)
    file_path, file_id = data_controller.generate_unique_filepath(
        orig_file_name=file.filename,
        project_id=project_id
    )
    try:
        async with aiofiles.open(file_path, "wb") as f:
            while chunk := await file.read(app_settings.CHUNK_SIZE):
                await f.write(chunk)
    except Exception as e:

        logger.error(f"Error while uploading file: {e}")

        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "signal": ResponseSignal.FILE_UPLOAD_FAILED.value
            }
        )

    return JSONResponse(
            content={
                "signal": ResponseSignal.FILE_UPLOAD_SUCCESS.value,
                "file_id": file_id
            }
        )   
        