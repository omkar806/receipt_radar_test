from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "Gmail Extractor"
    MAX_CONCURRENT_THREADS: int = 20
    BATCH_SIZE: int = 100
    ATTACHMENT_FOLDER: str = "attachments"

settings = Settings()