from models.certificate_data import CertificateData
from models.certificate_data import CertificateDataCertId, CertificateDataUserId
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
            print("Certificate Creation failed")
            return
        print(key_and_certificate_pem)
        await self.repo.upload_certificate(certificate_id=certificate_id, file_bytes=key_and_certificate_pem)
        await self.repo.upload_certificate_file(certificate_id=certificate_id, file_bytes=key_and_certificate_pem)

    async def create_certificate(self, data: CertificateDataCertId) -> BackgroundTask:
        return BackgroundTask(self.__create_certificate_in_background, data)

