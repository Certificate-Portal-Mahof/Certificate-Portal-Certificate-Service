from pydantic import BaseModel
from datetime import datetime


class CertificateData(BaseModel):
    certificate_id: str
    country_name: str
    state_or_province_name: str
    locality_name: str
    organization_name: str
    organizational_unit_name: str
    common_name: str
    email_address: str
    domain_names: list[str]
    ip_addresses: list[str]
    expiration_date: datetime
