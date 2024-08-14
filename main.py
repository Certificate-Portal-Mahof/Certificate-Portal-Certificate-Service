from litestar import Litestar, get
import uvicorn

from settings import Settings
import asyncio
from routers.certificates_operations.certificate_operations_router import router as certificate_operations_router
from tools.rabbitmq.rabbitmq_manager import RabbitMQManager

settings = Settings()


@get("/")
async def hello_world() -> str:
    return "Hello, world!"


async def startup() -> None:
    asyncio.get_event_loop().set_debug(settings.is_dev)
    RabbitMQManager().init(host=settings.rabbitmq_host)
    await RabbitMQManager().connect()


async def shutdown() -> None:
    await RabbitMQManager().close()


app = Litestar(route_handlers=[hello_world, certificate_operations_router], on_startup=[startup],
               on_shutdown=[shutdown])

if __name__ == "__main__":
    uvicorn.run(app=settings.app, host=settings.host, port=settings.port, reload=settings.reload, loop="asyncio")
