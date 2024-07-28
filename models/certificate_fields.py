from pydantic import BaseModel


class CertificateFields(BaseModel):
    country_name: str
    state_or_province_name: str
    locality_name: str
    organization_name: str
    organizational_unit_name: str
    common_name: str
    email_address: str
    dns_names: list[str]
    ip_addresses: list[str]
