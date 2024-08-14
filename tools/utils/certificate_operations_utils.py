import asyncio
import subprocess
import textwrap
from datetime import datetime

import aiofiles
from functools import partial
from models.certificate_data import CertificateData
from tools.file_names import FileNames
from config import ROOT_CA_CERTIFICATE_PATH, ROOT_CA_KEY_PATH, ROOT_CA_PASSCODE


def run_process(cmd):
    subprocess.run(cmd, text=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


class CertificateOperationsUtils:
    async def create_extension_file(self, certificate_data: CertificateData, certificate_filenames: FileNames):
        any_alt_names = True
        if len(certificate_data.domain_names) + len(certificate_data.ip_addresses) == 0:
            any_alt_names = False

        # Generate the configuration file content
        config_content = textwrap.dedent("""authorityKeyIdentifier=keyid,issuer
                                            basicConstraints=CA:FALSE
                                            keyUsage = digitalSignature, nonRepudiation, keyEncipherment, dataEncipherment
                                            """)

        if any_alt_names:
            config_content += textwrap.dedent("""subjectAltName = @alt_names
                                                 
                                                 [alt_names]\n""")
            # Add DNS names to the configuration
            for i, dns in enumerate(certificate_data.domain_names, start=1):
                config_content += f"DNS.{i} = {dns}\n"

            # Add IP addresses to the configuration
            for i, ip in enumerate(certificate_data.ip_addresses, start=1):
                config_content += f"IP.{i} = {ip}\n"

        try:
            # Write the configuration content to a file
            async with aiofiles.open(certificate_filenames.get_ext_filepath(), "w") as extension_file:
                await extension_file.write(config_content)
            print(f"Extension file generated: {certificate_filenames.get_ext_filepath()}")
        except IOError as e:
            print(f"IOError while writing the extension file: {e}")
            raise e
        except Exception as e:
            print(f"An unexpected error occurred while writing the extension file: {e}")
            raise e

    async def create_csr_and_key_files(self, certificate_data: CertificateData, certificate_filenames: FileNames):
        openssl_command = [
            "openssl", "req", "-new", "-nodes",
            "-out", certificate_filenames.get_csr_filepath(),
            "-newkey", "rsa:4096",
            "-keyout", certificate_filenames.get_key_filepath(),
            "-subj", f"/C={certificate_data.country_name}"
                     f"/ST={certificate_data.state_or_province_name}"
                     f"/L={certificate_data.locality_name}"
                     f"/O={certificate_data.organization_name}"
                     f"/OU={certificate_data.organizational_unit_name}"
                     f"/CN={certificate_data.common_name}"
                     f"/emailAddress={certificate_data.email_address}"
        ]

        try:
            partial_process = partial(run_process, openssl_command)
            await asyncio.get_event_loop().run_in_executor(None, partial_process)
            print(
                f"CSR and key generated: {certificate_filenames.get_csr_filepath()}, "
                f"{certificate_filenames.get_key_filepath()}")
        except subprocess.CalledProcessError as e:
            print(f"Error generating CSR and key: {e}")
            print(e.stderr)
            raise e
        except Exception as e:
            print(f"An unexpected error occurred while generating CSR and key: {e}")
            raise e

    async def create_crt_file(self, certificate_data: CertificateData, certificate_filenames: FileNames):
        certificate_expiration_date: datetime = certificate_data.expiration_date.replace(tzinfo=None)
        current_date = datetime.now()
        expiration_days = (certificate_expiration_date - current_date).days

        if expiration_days <= 0:
            raise ValueError("The expiration date must be in the future.")

        openssl_command = [
            "openssl", "x509", "-req",
            "-in", certificate_filenames.get_csr_filepath(),
            "-CA", ROOT_CA_CERTIFICATE_PATH,
            "-CAkey", ROOT_CA_KEY_PATH,
            "-CAcreateserial",
            "-out", certificate_filenames.get_crt_filepath(),
            "-days", str(expiration_days),
            "-sha256",
            "-extfile", certificate_filenames.get_ext_filepath(),
            "-passin", f"pass:{ROOT_CA_PASSCODE}"
        ]

        try:
            partial_process = partial(run_process, openssl_command)
            await asyncio.get_event_loop().run_in_executor(None, partial_process)
            print(f"Certificate generated: {certificate_filenames.get_crt_filepath()}")
        except subprocess.CalledProcessError as e:
            print(f"Error generating CSR and key: {e}")
            print(e.stderr)
            raise e
        except Exception as e:
            print(f"An unexpected error occurred while generating certificate: {e}")
            raise e

    async def create_pem_file(self, certificate_filenames: FileNames):
        try:
            async with aiofiles.open(certificate_filenames.get_key_filepath(), "r") as key_file:
                key_data = await key_file.read()

            async with aiofiles.open(certificate_filenames.get_crt_filepath(), "r") as crt_file:
                crt_data = await crt_file.read()

            async with aiofiles.open(certificate_filenames.get_pem_filepath(), "w") as pem_file:
                await pem_file.write(key_data)
                await pem_file.write('\n')
                await pem_file.write(crt_data)

            print(f"PEM file generated: {certificate_filenames.get_pem_filepath()}")
        except IOError as e:
            print(f"IOError while writing the extension file: {e}")
            raise e
        except Exception as e:
            print(f"An unexpected error occurred while writing the extension file: {e}")
            raise e

    async def create_certificate(self, certificate_data: CertificateData) -> FileNames | None:
        certificate_filenames = FileNames()

        try:
            await self.create_csr_and_key_files(certificate_data, certificate_filenames)
            await self.create_extension_file(certificate_data, certificate_filenames)
            await self.create_crt_file(certificate_data, certificate_filenames)
            await self.create_pem_file(certificate_filenames)

            return certificate_filenames
        except subprocess.CalledProcessError as e:
            print(f"Error during certificate creation process: {e}")
            return None
        except Exception as e:
            print(e)
            return None
