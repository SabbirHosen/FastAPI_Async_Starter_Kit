from dotenv import load_dotenv
import os
from urllib.parse import quote_plus


class Settings:
    def __init__(self):
        load_dotenv()

        self.RETRY_ATTEMPTS = 3
        self.RETRY_DELAY = 5

        self.EMAIL_HOST = os.getenv('EMAIL_HOST')
        self.EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
        self.EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
        self.EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
        self.EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS')
        self.EMAIL_RECEIVER = os.getenv('EMAIL_RECEIVER')

        self.LOG_DIR = "."

        self.DB_URL: str = os.getenv("DB_URL", "postgresql+asyncpg://postgres:1234@localhost/dbname")
        self.SECRET_KEY: str = "your-secret-key"
        self.ALGORITHM: str = "HS256"
        self.ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
        self.REFRESH_TOKEN_EXPIRE_DAYS: int = 29

        self.DATABASE_USER: str = os.getenv("DATABASE_USER")
        self.DATABASE_PASSWORD: str = os.getenv("DATABASE_PASSWORD")
        self.DATABASE_HOST: str = os.getenv("DATABASE_HOST")
        self.DATABASE_PORT: str = os.getenv("DATABASE_PORT")
        self.DATABASE_NAME: str = os.getenv("DATABASE_NAME")

        self.CORS_ALLOW_ORIGINS: list[str] = os.getenv("CORS_ALLOW_ORIGINS", "*").split(",")
        self.CORS_ALLOW_CREDENTIALS: bool = os.getenv("CORS_ALLOW_CREDENTIALS", "true").lower() == "true"
        self.CORS_ALLOW_METHODS: list[str] = os.getenv("CORS_ALLOW_METHODS", "*").split(",")
        self.CORS_ALLOW_HEADERS: list[str] = os.getenv("CORS_ALLOW_HEADERS", "*").split(",")

    @property
    def get_database_url(self):
        database_url: str = os.getenv("DATABASE_URL")
        if database_url is None:
            if self.DATABASE_USER and self.DATABASE_PASSWORD and self.DATABASE_HOST and self.DATABASE_PORT and self.DATABASE_NAME:
                encoded_password = quote_plus(self.DATABASE_PASSWORD)
                database_url = (
                    f"postgresql+asyncpg://{self.DATABASE_USER}:{encoded_password}@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"
                )
            else:
                raise Exception("DATABASE configuration environment variable is not set")
        return database_url


settings = Settings()
