from litestar import Router, post
from typing import Annotated
from litestar.response import Response

from models.certificate_data import CertificateDataCertId


@post("/create-certificate", status_code=status_codes.HTTP_200_OK)
async def create_certificate(data: Annotated[CertificateDataCertId, Body()]) -> Response:
    create_certificate_background_task = await CertificateOperationsService().create_certificate(data)
    return Response(content="Certificate Creation Submitted Successfully",
                    background=create_certificate_background_task)


router = Router(path="/cert-ops", route_handlers=[create_certificate])
