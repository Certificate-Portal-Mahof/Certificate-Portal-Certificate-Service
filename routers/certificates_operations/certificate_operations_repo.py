from bson import ObjectId
from litestar import status_codes
from litestar.exceptions import HTTPException
from pymongo.errors import DuplicateKeyError

from db.db import MongoConnector
from models.certificate_data import CertificateDataUserId


class CertificateOperationsRepo:
    def __init__(self):
        self.db = MongoConnector().db
        self.fs = MongoConnector().fs

    async def upload_certificate_file(self, certificate_id: str, file_bytes: bytes) -> None:
        await self.fs.upload_from_stream(filename=certificate_id, source=file_bytes)

    async def create_certificate(self, certificate: CertificateDataUserId) -> ObjectId:
        try:
            new_certificate_details = await self.db["certificates"].insert_one(certificate.model_dump())
            return new_certificate_details.inserted_id
        except DuplicateKeyError:
            raise HTTPException(status_code=status_codes.HTTP_409_CONFLICT, detail="Certificate already exists.")