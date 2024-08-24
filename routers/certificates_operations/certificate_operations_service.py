from models.certificate_data import CertificateDataCertId, CertificateDataUserId
from models.certificate_file import CertificateFile
from routers.certificates_operations.certificate_operations_repo import CertificateOperationsRepo
from tools.utils.certificate_operations_utils import CertificateOperationsUtils
from litestar.background_tasks import BackgroundTask


class CertificateOperationsService:
    def __init__(self) -> None:
        self.repo = CertificateOperationsRepo()
        self.certificate_operation_utils = CertificateOperationsUtils()

    async def __create_certificate_in_background(self, data: CertificateDataCertId) -> None:
        certificate_id = data.certificate_id

        key_and_certificate_pem = await self.certificate_operation_utils.create_certificate(data)
        if key_and_certificate_pem is None:
            print("Certificate Creation Failed")
            return
        print(key_and_certificate_pem)
        await self.repo.upload_certificate_file(certificate_id=certificate_id, file_bytes=key_and_certificate_pem)

    async def create_certificate(self, data: CertificateDataCertId) -> BackgroundTask:
        return BackgroundTask(self.__create_certificate_in_background, data)

    async def __upload_certificate_in_background(self, certificate_file: CertificateFile) -> None:
        pem_content = await certificate_file.pem_file.read()
        await certificate_file.pem_file.close()

        certificate_metadata = await self.certificate_operation_utils.convert_certificate_to_object(pem_content)
        if certificate_metadata is None:
            print("Certificate Upload Failed")
            return

        user_id = certificate_file.user_id
        cert_name = certificate_file.cert_name
        certificate_data = CertificateDataUserId(user_id=user_id, cert_name=cert_name,
                                                 **(certificate_metadata.model_dump()))

        certificate_object_id = await self.repo.create_certificate(certificate_data)
        certificate_id = str(certificate_object_id)
        await self.repo.upload_certificate_file(certificate_id=certificate_id, file_bytes=pem_content)

    async def upload_certificate(self, certificate_file: CertificateFile) -> BackgroundTask:
        return BackgroundTask(self.__upload_certificate_in_background, certificate_file)
