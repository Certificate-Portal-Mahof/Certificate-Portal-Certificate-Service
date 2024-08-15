import asyncio
import os

import aiofiles

from models.certificate_data import CertificateData
from routers.certificates_operations.certificate_operations_repo import CertificateOperationsRepo
from tools.utils.certificate_operations_utils import CertificateOperationsUtils
from litestar.background_tasks import BackgroundTask
from tools.file_names import FileNames


async def remove_files(certificate_filenames: FileNames) -> None:
    event_loop = asyncio.get_event_loop()
    try:
        tasks = [event_loop.run_in_executor(None, os.remove, path) for path in
                 certificate_filenames.get_all_files_paths()]
        await asyncio.gather(*tasks)
    except FileNotFoundError as e:
        print(f"File not found: {e}")


class CertificateOperationsService:
    def __init__(self) -> None:
        self.repo = CertificateOperationsRepo()
        self.certificate_operation_utils = CertificateOperationsUtils()

    async def create_certificate(self, data: CertificateData) -> BackgroundTask:
        return BackgroundTask(self.create_certificate_in_background, data)

    async def create_certificate_in_background(self, data: CertificateData) -> None:
        certificate_id = data.certificate_id
        certificate_filenames: (FileNames | None) = await self.certificate_operation_utils.create_certificate(data)
        if certificate_filenames is None:
            return

        async with aiofiles.open(certificate_filenames.get_pem_filepath(), "rb") as file:
            file_bytes = await file.read()

        await remove_files(certificate_filenames)

        await self.repo.upload_certificate(certificate_id=certificate_id, file_bytes=file_bytes)
