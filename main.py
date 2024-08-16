import os

from litestar import Litestar, get
import uvicorn

from db.db import MongoConnector
from settings import Settings
import asyncio
from routers.certificates_operations.certificate_operations_router import router as certificate_operations_router
from tools.utils.certificate_operations_utils import CertificateOperationsUtils

settings = Settings()


@get("/")
async def hello_world() -> str:
    return "Hello, world!"


async def startup() -> None:
    asyncio.get_event_loop().set_debug(settings.is_dev)

    MongoConnector().init(mongodb_uri=os.getenv("MONGODB_URI"), db_name=os.getenv("DB_NAME"))

    CertificateOperationsUtils().init()


async def shutdown() -> None:
    MongoConnector().close_connection()


app = Litestar(route_handlers=[hello_world, certificate_operations_router], on_startup=[startup],
               on_shutdown=[shutdown])

if __name__ == "__main__":
    uvicorn.run(app=settings.app, host=settings.host, port=settings.port, reload=settings.reload, loop="asyncio")
