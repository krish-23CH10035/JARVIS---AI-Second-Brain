"""Configuration module for JARVIS AI System."""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class GroqConfig(BaseSettings):
    """Groq API configuration."""
    api_key: str = Field(default="", alias="GROQ_API_KEY")
    chat_deployment: str = Field(default="llama3-70b-8192", alias="GROQ_CHAT_DEPLOYMENT")

    class Config:
        env_file = ".env"
        extra = "ignore"


class CohereConfig(BaseSettings):
    """Cohere API configuration for embeddings."""
    api_key: str = Field(default="", alias="COHERE_API_KEY")
    embedding_model: str = Field(default="embed-english-v3.0", alias="COHERE_EMBEDDING_MODEL")
    embedding_dimensions: int = Field(default=1024, alias="COHERE_EMBEDDING_DIMENSIONS")

    class Config:
        env_file = ".env"
        extra = "ignore"


class AzureBlobConfig(BaseSettings):
    """Azure Blob Storage configuration."""
    connection_string: str = Field(default="", alias="AZURE_BLOB_CONNECTION_STRING")
    container_name: str = Field(default="documents", alias="AZURE_BLOB_CONTAINER_NAME")

    class Config:
        env_file = ".env"
        extra = "ignore"


class AzureDocIntelligenceConfig(BaseSettings):
    """Azure Document Intelligence configuration."""
    endpoint: str = Field(default="", alias="AZURE_DOC_INTELLIGENCE_ENDPOINT")
    api_key: str = Field(default="", alias="AZURE_DOC_INTELLIGENCE_API_KEY")

    class Config:
        env_file = ".env"
        extra = "ignore"


class AzureSpeechConfig(BaseSettings):
    """Azure Speech configuration."""
    key: str = Field(default="", alias="AZURE_SPEECH_KEY")
    region: str = Field(default="", alias="AZURE_SPEECH_REGION")
    tts_voice: str = Field(default="en-US-AndrewNeural", alias="AZURE_TTS_VOICE")
    tts_style: str = Field(default="chat", alias="AZURE_TTS_STYLE")
    tts_force_male: bool = Field(default=True, alias="AZURE_TTS_FORCE_MALE")

    class Config:
        env_file = ".env"
        extra = "ignore"


class DatabaseConfig(BaseSettings):
    """Database configuration."""
    database_url: str = Field(
        default="sqlite+aiosqlite:///jarvis.db",
        alias="DATABASE_URL"
    )

    class Config:
        env_file = ".env"
        extra = "ignore"


class WhapiConfig(BaseSettings):
    """Whapi (WhatsApp API) configuration."""
    token: str = Field(default="", alias="WHAPI_TOKEN")
    base_url: str = Field(default="https://gate.whapi.cloud/messages/text", alias="WHAPI_BASE_URL")
    default_country_code: str = Field(default="91", alias="WHAPI_DEFAULT_COUNTRY_CODE")
    timeout_seconds: int = Field(default=30, alias="WHAPI_TIMEOUT_SECONDS")
    max_retries: int = Field(default=2, alias="WHAPI_MAX_RETRIES")

    class Config:
        env_file = ".env"
        extra = "ignore"


class TwilioConfig(BaseSettings):
    """Twilio SMS configuration."""
    account_sid: str = Field(default="", alias="TWILIO_ACCOUNT_SID")
    auth_token: str = Field(default="", alias="TWILIO_AUTH_TOKEN")
    from_number: str = Field(default="", alias="TWILIO_FROM_NUMBER")
    messaging_service_sid: str = Field(default="", alias="TWILIO_MESSAGING_SERVICE_SID")
    default_country_code: str = Field(default="91", alias="TWILIO_DEFAULT_COUNTRY_CODE")
    simulate: bool = Field(default=False, alias="TWILIO_SIMULATE")

    class Config:
        env_file = ".env"
        extra = "ignore"


class AppConfig(BaseSettings):
    """Application-level configuration."""
    app_name: str = Field(default="JARVIS AI System", alias="APP_NAME")
    debug: bool = Field(default=False, alias="DEBUG")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    host: str = Field(default="0.0.0.0", alias="HOST")
    port: int = Field(default=8000, alias="PORT")
    secret_key: str = Field(default="change-me-in-production", alias="SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    jwt_expiry_minutes: int = Field(default=60, alias="JWT_EXPIRY_MINUTES")
    max_input_length: int = Field(default=4000, alias="MAX_INPUT_LENGTH")
    max_file_size_mb: int = Field(default=50, alias="MAX_FILE_SIZE_MB")
    chunk_size: int = Field(default=500, alias="CHUNK_SIZE")
    chunk_overlap: int = Field(default=100, alias="CHUNK_OVERLAP")
    top_k_results: int = Field(default=7, alias="TOP_K_RESULTS")
    appinsights_connection_string: str = Field(default="", alias="APPLICATIONINSIGHTS_CONNECTION_STRING")

    class Config:
        env_file = ".env"
        extra = "ignore"


class Settings:
    """Master settings container that aggregates all configuration sections."""

    def __init__(self):
        self.app = AppConfig()
        self.groq = GroqConfig()
        self.cohere = CohereConfig()
        self.azure_blob = AzureBlobConfig()
        self.azure_doc_intelligence = AzureDocIntelligenceConfig()
        self.azure_speech = AzureSpeechConfig()
        self.database = DatabaseConfig()
        self.whapi = WhapiConfig()
        self.twilio = TwilioConfig()

    def validate_core_services(self) -> dict:
        """Check which core services are configured and return status."""
        status = {
            "groq": bool(self.groq.api_key),
            "cohere": bool(self.cohere.api_key),
            "azure_blob": bool(self.azure_blob.connection_string),
            "azure_doc_intelligence": bool(
                self.azure_doc_intelligence.endpoint and self.azure_doc_intelligence.api_key
            ),
        }
        return status

    def is_production_ready(self) -> bool:
        """Check if all critical services are configured."""
        status = self.validate_core_services()
        return status["groq"] and status["cohere"]


# Global singleton
settings = Settings()
