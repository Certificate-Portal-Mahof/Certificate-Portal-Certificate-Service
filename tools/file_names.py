import uuid
from config import TEMP_FILES_FOLDER_PATH


class FileNames:
    file_name: str = ""

    def __init__(self, prefix="cert_"):
        unique_id = uuid.uuid4()
        self.file_name = f"{prefix}{unique_id}"

    def get_key_filename(self) -> str:
        return self.file_name + ".key"

    def get_key_filepath(self) -> str:
        return TEMP_FILES_FOLDER_PATH + "/key_files/" + self.get_key_filename()

    def get_csr_filename(self) -> str:
        return self.file_name + ".csr"

    def get_csr_filepath(self) -> str:
        return TEMP_FILES_FOLDER_PATH + "/csr_files/" + self.get_csr_filename()

    def get_crt_filename(self) -> str:
        return self.file_name + ".crt"

    def get_crt_filepath(self) -> str:
        return TEMP_FILES_FOLDER_PATH + "/crt_files/" + self.get_crt_filename()

    def get_ext_filename(self) -> str:
        return self.file_name + ".v3.ext"

    def get_ext_filepath(self) -> str:
        return TEMP_FILES_FOLDER_PATH + "/ext_files/" + self.get_ext_filename()

    def get_pem_filename(self) -> str:
        return self.file_name + ".pem"

    def get_pem_filepath(self) -> str:
        return TEMP_FILES_FOLDER_PATH + "/pem_files/" + self.get_pem_filename()

    def get_all_files_paths(self) -> list[str]:
        return [
            self.get_csr_filepath(),
            self.get_key_filepath(),
            self.get_ext_filepath(),
            self.get_crt_filepath(),
            self.get_pem_filepath()
        ]
