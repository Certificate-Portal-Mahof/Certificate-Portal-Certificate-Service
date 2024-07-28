from typing import Annotated

from litestar import Router, post
from litestar.params import Body
from models.certificate_fields import CertificateFields
from tools.utils.certificate_operations_utils import CertificateOperationsUtils


@post("/create-certificate")
async def create_certificate(data: CertificateFields) -> None:
    print(type(data))
    print(data.dns_names)

    CertificateOperationsUtils().create_certificate(certificate_fields=data)


router = Router(path="/cert-ops", route_handlers=[create_certificate])
