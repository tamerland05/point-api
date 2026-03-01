import asyncio
import logging
import sys
from concurrent.futures import ProcessPoolExecutor
from contextlib import asynccontextmanager
from decimal import getcontext

from starlette.responses import JSONResponse
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from tortoise.contrib.fastapi import register_tortoise

from point.config import settings
from point.controllers.pooling import stop_pooling, run_pooling_process
from point.errors import APIException
from point.routes import router

logger = logging.getLogger()
logger.setLevel(logging.INFO)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
formatter = logging.Formatter(
    "%(asctime)s,%(msecs)03d %(levelname)s [%(filename)s:%(lineno)d] %(message)s",
    "%Y-%m-%d:%H:%M:%S",
)
handler.setFormatter(formatter)
logger.handlers = [handler]

APP_BASE = "/api/v1/point"


pooling_executor = ProcessPoolExecutor(max_workers=1)


@asynccontextmanager
async def lifespan(_: FastAPI):
    getcontext().prec = 64
    loop = asyncio.get_running_loop()

    loop.run_in_executor(pooling_executor, run_pooling_process)

    yield

    stop_pooling()


app = FastAPI(
    title="Pont service API",
    debug=True,
    docs_url=f"{APP_BASE}/docs",
    redoc_url=None,
    version="0.0.1",
    openapi_url=f"{APP_BASE}/point.json",
    lifespan=lifespan,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(APIException)
async def api_exception_handler(_: Request, exc: APIException) -> JSONResponse:
    err = exc.error
    content = {"error": err.name.lower()}
    if err.message is not None:
        content["message"] = err.message

    return JSONResponse(status_code=err.code, content=content)


@app.exception_handler(HTTPException)
async def http_exception_handler(_: Request, exc: HTTPException) -> JSONResponse:
    logging.exception(exc)
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail},
    )


@app.exception_handler(Exception)
async def exception_handler(_: Request, exc: Exception) -> JSONResponse:
    logging.exception(exc)
    return JSONResponse(
        status_code=400,
        content={"error": str(exc)},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_: Request, exc: RequestValidationError):
    logging.exception(exc)
    content = {
        "message": str(exc),
        "error": "validation-error",
        "fields": [
            {
                "field": er["loc"][1] if len(er["loc"]) > 1 else er["loc"],
                "message": er["msg"],
                "error": er["type"].replace("_", "-"),
            }
            for er in exc.errors()
        ],
    }
    logging.error(exc.errors())

    return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content=content)


app.include_router(router, prefix=APP_BASE)

Instrumentator().instrument(app).expose(
    app=app,
    endpoint=APP_BASE + "/metrics",
    tags=["Aux endpoints"],
)
register_tortoise(app, add_exception_handlers=True, config=settings.tortoise_orm, generate_schemas=False)
