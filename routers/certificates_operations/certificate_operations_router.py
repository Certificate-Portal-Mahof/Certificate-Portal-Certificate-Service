from typing import Annotated

from litestar import Router, post, MediaType, status_codes
from litestar.enums import RequestEncodingType
from litestar.params import Body
from litestar.response import Response

from models.certificate_data import CertificateDataCertId
from models.certificate_file import CertificateFile
from routers.certificates_operations.certificate_operations_service import CertificateOperationsService


@post("/create-certificate", status_code=status_codes.HTTP_200_OK)
async def create_certificate(data: Annotated[CertificateDataCertId, Body()]) -> Response:
    create_certificate_background_task = await CertificateOperationsService().create_certificate(data)
    return Response(content="Certificate Creation Submitted Successfully",
                    background=create_certificate_background_task)


@post("/upload-certificate", status_code=status_codes.HTTP_200_OK, media_type=MediaType.TEXT)
async def upload_certificate(data: Annotated[CertificateFile, Body(media_type=RequestEncodingType.MULTI_PART)],
                             ) -> Response:
    upload_certificate_background_task = await CertificateOperationsService().upload_certificate(data)

    return Response(content="Certificate Uploading Submitted Successfully",
                    background=upload_certificate_background_task)


router = Router(path="/cert-ops", route_handlers=[create_certificate, upload_certificate])
