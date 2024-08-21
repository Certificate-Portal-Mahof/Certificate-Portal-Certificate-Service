from datetime import datetime, timedelta
from ipaddress import IPv4Address
from typing import Any, Optional

from cryptography import x509
from cryptography.hazmat._oid import NameOID
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey
from cryptography.x509 import Certificate

from config import ROOT_CA_CERTIFICATE_PATH, ROOT_CA_KEY_PATH, ROOT_CA_PASSCODE
from models.certificate_data import CertificateDataCertId, CertificateMetaData
from tools.singleton import Singleton


class CertificateOperationsUtils(metaclass=Singleton):
    cryptography_default_backend: Any = None
    ca_cert: Certificate = None
    ca_key: RSAPrivateKey = None

    def init(self) -> None:
        self.cryptography_default_backend = default_backend()
        self.ca_cert, self.ca_key = self.__load_ca_certificate_and_key()

    def __load_ca_certificate_and_key(self) -> [Certificate, RSAPrivateKey]:
        root_ca_passcode_bytes = ROOT_CA_PASSCODE.encode()

        with open(ROOT_CA_CERTIFICATE_PATH, "rb") as cert_file:
            ca_cert_data = cert_file.read()
            ca_cert = x509.load_pem_x509_certificate(data=ca_cert_data, backend=self.cryptography_default_backend)

        with open(ROOT_CA_KEY_PATH, "rb") as key_file:
            ca_key_data = key_file.read()
            ca_key = serialization.load_pem_private_key(ca_key_data, root_ca_passcode_bytes,
                                                        self.cryptography_default_backend)

        return ca_cert, ca_key

    @staticmethod
    def __get_expiration_days(expiration_date: datetime) -> int:
        certificate_expiration_date: datetime = expiration_date.replace(tzinfo=None)
        current_date = datetime.now()
        expiration_days = (certificate_expiration_date - current_date).days
        return expiration_days

    async def __generate_certificate(self, certificate_data: CertificateDataCertId) -> [bytes, bytes]:
        try:
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048,
                backend=self.cryptography_default_backend
            )

            subject = x509.Name([
                x509.NameAttribute(NameOID.COUNTRY_NAME, certificate_data.country_name),
                x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, certificate_data.state_or_province_name),
                x509.NameAttribute(NameOID.LOCALITY_NAME, certificate_data.locality_name),
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, certificate_data.organization_name),
                x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, certificate_data.organizational_unit_name),
                x509.NameAttribute(NameOID.EMAIL_ADDRESS, certificate_data.email_address),
                x509.NameAttribute(NameOID.COMMON_NAME, certificate_data.common_name),
            ])

            expiration_days = CertificateOperationsUtils.__get_expiration_days(certificate_data.expiration_date)

            certificate_builder = x509.CertificateBuilder().subject_name(
                subject
            ).issuer_name(
                self.ca_cert.subject
            ).public_key(
                private_key.public_key()
            ).serial_number(
                x509.random_serial_number()
            ).not_valid_before(
                datetime.utcnow()
            ).not_valid_after(
                datetime.utcnow() + timedelta(days=expiration_days)
            ).add_extension(
                x509.SubjectAlternativeName([x509.DNSName(dns) for dns in certificate_data.domain_names] +
                                            [x509.IPAddress(IPv4Address(ip)) for ip in certificate_data.ip_addresses]),
                critical=False,
            )

            certificate = certificate_builder.sign(self.ca_key, hashes.SHA256(), self.cryptography_default_backend)

            private_key_pem = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption()
            )

            certificate_pem = certificate.public_bytes(serialization.Encoding.PEM)

            return private_key_pem, certificate_pem
        except Exception as e:
            print(f"Unknown exception while creating a certificate: {e}")
            print(type(e))

    async def create_certificate(self, certificate_data: CertificateDataCertId) -> Optional[bytes]:
        try:
            private_key_pem, certificate_pem = await self.__generate_certificate(certificate_data=certificate_data)
            key_and_certificate_pem = certificate_pem + b'\n' + private_key_pem
            return key_and_certificate_pem
        except Exception as e:
            print(e)
            return None
