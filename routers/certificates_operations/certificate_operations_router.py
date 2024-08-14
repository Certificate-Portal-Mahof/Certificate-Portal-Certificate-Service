from litestar import Router, post
from litestar.response import Response
from models.certificate_data import CertificateData
from routers.certificates_operations.certificate_operations_service import CertificateOperationsService, remove_files


@post("/create-certificate")
async def create_certificate(data: CertificateData) -> Response:
    create_certificate_background_task = await CertificateOperationsService().create_certificate(data)
    return Response(content="Certificate Creation Submitted Successfully",
                    background=create_certificate_background_task)


router = Router(path="/cert-ops", route_handlers=[create_certificate])
