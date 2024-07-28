from litestar import Litestar, get
import uvicorn

from models.certificate_fields import CertificateFields
from settings import Settings
import asyncio
from routers.certificates_operations.certificate_operations_router import router as certificate_operations_router
from tools.utils.certificate_operations_utils import CertificateOperationsUtils

settings = Settings()


@get("/")
async def hello_world() -> str:
    certificate_fields = CertificateFields(
        country_name="US",
        state_or_province_name="California",
        locality_name="San Francisco",
        organization_name="Example Org",
        organizational_unit_name="IT",
        common_name="example.com",
        email_address="admin@example.com",
        dns_names=["example.com", "www.example.com"],
        ip_addresses=["192.168.1.1", "10.0.0.1"],
    )
    try:
        CertificateOperationsUtils().create_certificate(certificate_fields=certificate_fields)
    except Exception as e:
        print(e)
    return "Hello, world!"


def startup() -> None:
    asyncio.get_event_loop().set_debug(settings.is_dev)


app = Litestar(route_handlers=[hello_world, certificate_operations_router], on_startup=[startup])

if __name__ == "__main__":
    uvicorn.run(app=settings.app, host=settings.host, port=settings.port, reload=settings.reload)
