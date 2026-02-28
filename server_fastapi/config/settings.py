from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PORT: int = 5000
    MONGO_URI: str
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    WEB_BASE_URL: str = "http://localhost:5173"
    SMTP_HOST: str
    SMTP_PORT: int = 587
    SMTP_SECURE: int = 0
    SMTP_USER: str
    SMTP_PASS: str
    MAIL_FROM: str = '"LexiBot <no-reply@lexibot.ai>"'
    ADMIN_EMAIL: str
    ADMIN_PASSWORD: str
    ADMIN_NAME: str
    
    # AI/ML Configuration
    CEREBRAS_API_KEY: str = "your_cerebras_api_key_here"  # Cerebras API key
    CEREBRAS_BASE_URL: str = "https://api.cerebras.ai/v1"
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    LLM_MODEL: str = "llama-3.3-70b"
    MAX_TOKENS: int = 65536
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    TOP_K_RETRIEVAL: int = 5
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()

def get_settings() -> Settings:
    """Get application settings."""
    return settings

