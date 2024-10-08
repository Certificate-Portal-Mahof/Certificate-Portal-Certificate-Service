import os
from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    is_dev: bool = os.getenv("IS_DEV").lower() == "true"
    app: str = "main:app"
    host: str = "127.0.0.1" if is_dev else "0.0.0.0"
    port: int = 9200
    reload: bool = False
    allow_origins: List[str] = ["http://localhost:5173"] if is_dev else ["*"]
    allow_methods: List[str] = ["*"]
    allow_credentials: bool = True
    allow_headers: List[str] = ["*"]
