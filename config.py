import os

TEMP_FILES_FOLDER_PATH = "./temp_files"
ROOT_CA_CERTIFICATE_PATH = "./root_ca_files/RootCA.crt"
ROOT_CA_KEY_PATH = "./root_ca_files/RootCA.key"
ROOT_CA_PASSCODE = os.getenv("ROOT_CA_PASSCODE")
