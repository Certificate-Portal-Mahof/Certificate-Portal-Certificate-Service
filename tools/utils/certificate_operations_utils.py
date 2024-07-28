import subprocess
from models.certificate_fields import CertificateFields
from tools.file_names import FileNames
from config import ROOT_CA_CERTIFICATE_PATH, ROOT_CA_KEY_PATH, ROOT_CA_PASSCODE
class CertificateOperationsUtils:

    def create_extension_file(self, certificate_fields: CertificateFields, certificate_filenames: FileNames):
        # Generate the configuration file content
        config_content = """
        authorityKeyIdentifier=keyid,issuer
        basicConstraints=CA:FALSE
        keyUsage = digitalSignature, nonRepudiation, keyEncipherment, dataEncipherment
        subjectAltName = @alt_names

        [alt_names]
        """

        # Add DNS names to the configuration
        for i, dns in enumerate(certificate_fields.dns_names, start=1):
            config_content += f"DNS.{i} = {dns}\n"

        # Add IP addresses to the configuration
        for i, ip in enumerate(certificate_fields.ip_addresses, start=1):
            config_content += f"IP.{i} = {ip}\n"

        try:
            # Write the configuration content to a file
            with open(certificate_filenames.get_ext_filepath(), "w") as extension_file:
                extension_file.write(config_content)
            print(f"Extension file generated: {certificate_filenames.get_ext_filepath()}")
        except IOError as e:
            print(f"IOError while writing the extension file: {e}")
        except Exception as e:
            print(f"An unexpected error occurred while writing the extension file: {e}")

    def create_csr_and_key_files(self, certificate_fields: CertificateFields, certificate_filenames: FileNames):
        openssl_command = [
            "openssl", "req", "-new", "-nodes",
            "-out", certificate_filenames.get_csr_filepath(),
            "-newkey", "rsa:4096",
            "-keyout", certificate_filenames.get_key_filepath(),
            "-subj", f"/C={certificate_fields.country_name}/ST={certificate_fields.state_or_province_name}/L={certificate_fields.locality_name}/O={certificate_fields.organization_name}/OU={certificate_fields.organizational_unit_name}/CN={certificate_fields.common_name}/emailAddress={certificate_fields.email_address}"
        ]

        try:
            subprocess.run(openssl_command, check=True, text=True, stderr=subprocess.PIPE)
            print(f"CSR and key generated: {certificate_filenames.get_csr_filepath()}, {certificate_filenames.get_key_filepath()}")
        except subprocess.CalledProcessError as e:
            print(f"Error generating CSR and key: {e}")
            print(e.stderr)
        except Exception as e:
            print(f"An unexpected error occurred while generating CSR and key: {e}")

    def create_crt_file(self, certificate_filenames: FileNames):
        openssl_command = [
            "openssl", "x509", "-req",
            "-in", certificate_filenames.get_csr_filepath(),
            "-CA", ROOT_CA_CERTIFICATE_PATH,
            "-CAkey", ROOT_CA_KEY_PATH,
            "-CAcreateserial",
            "-out", certificate_filenames.get_crt_filepath(),
            "-days", "730",
            "-sha256",
            "-extfile", certificate_filenames.get_ext_filepath(),
            "-passin", f"pass:{ROOT_CA_PASSCODE}"
        ]

        try:
            subprocess.run(openssl_command, check=True, text=True, stderr=subprocess.PIPE)
            print(f"Certificate generated: {certificate_filenames.get_crt_filepath()}")

        except subprocess.CalledProcessError as e:
            print(f"Error generating certificate: {e}")
            print(e.stderr)
        except Exception as e:
            print(f"An unexpected error occurred while generating certificate: {e}")

    def create_certificate(self, certificate_fields: CertificateFields):
        certificate_filenames = FileNames()

        try:
            self.create_csr_and_key_files(certificate_fields, certificate_filenames)
            self.create_extension_file(certificate_fields, certificate_filenames)
            self.create_crt_file(certificate_filenames)

            # Optionally, delete the temporary files after using them
            # try:
            #     os.remove(certificate_filenames.get_csr_filepath())
            #     os.remove(certificate_filenames.get_key_filepath())
            #     os.remove(certificate_filenames.get_ext_filepath())
            # except OSError as e:
            #     print(f"Error removing temporary files: {e}")
        except subprocess.CalledProcessError as e:
            print(f"Error during certificate creation process: {e}")
        except Exception as e:
            print(f"An unexpected error occurred during certificate creation process: {e}")
