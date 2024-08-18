from db.db import MongoConnector


class CertificateOperationsRepo:
    def __init__(self):
        self.db = MongoConnector().db
        self.fs = MongoConnector().fs

    async def upload_certificate(self, certificate_id: str, file_bytes: bytes) -> None:
        await MongoConnector().fs.upload_from_stream(filename=certificate_id, source=file_bytes)
