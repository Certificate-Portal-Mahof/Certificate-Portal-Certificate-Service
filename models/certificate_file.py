from litestar.datastructures import UploadFile
from pydantic import BaseModel, BaseConfig


class CertificateFile(BaseModel):
    pem_file: UploadFile
    user_id: str
    cert_name: str

    class Config(BaseConfig):
        arbitrary_types_allowed = True
