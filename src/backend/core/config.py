from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


_ENV_FILE = Path(__file__).resolve().parents[3] / ".env"

class Settings(BaseSettings):

    model_config = SettingsConfigDict(
        env_file=str(_ENV_FILE), 
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # --- OpenRouter API ---
    openrouter_api_key: str = Field(..., description="OpenRouter API key (required)")
    openrouter_base_url: str = Field(
        default="https://openrouter.ai/api/v1",
        description="OpenRouter API base URL",
    )

    # --- LLM Parameters ---
    llm_model: str = Field(
        default="arcee-ai/trinity-large-preview:free",
        description="Model identifier in OpenRouter format (provider/model-name)",
    )
    llm_max_tokens: int = Field(
        default=1024,
        ge=64,
        le=4096,
        description="Maximum tokens in LLM response",
    )
    llm_temperature: float = Field(
        default=0.3,
        ge=0.0,
        le=1.0,
        description="LLM temperature — lower is more conservative and factual",
    )

    # --- App Settings ---
    app_host: str = Field(default="0.0.0.0")
    app_port: int = Field(default=8000)
    app_debug: bool = Field(default=False)

    # --- Session Settings ---
    session_max_turns: int = Field(
        default=20,
        ge=1,
        le=100,
        description="Max conversation turns kept in memory per session",
    )


     # --- RAG Settings ---
    vector_store_path: str = Field(
        default="./vector_store",
        description="The path where the vector store data will be saved",
    )
    collection_name: str = Field(
        default="liver_care_docs",
    )
    embedding_model: str = Field(
        default="paraphrase-multilingual-MiniLM-L12-v2",
        description="HuggingFace embedding model identifier for both arabic and english languages",
    )
    chunk_size: int = Field(
        default=500,
    )
    chunk_overlap: int = Field(
        default=50,
    )
    retrieval_top_k: int = Field(
        default=3
    )
    upload_dir: str = Field(
        default="./uploads",
        description="The path where the PDFs will be uploaded",
    )



    # --- Logging Settings ---
    log_level: str = Field(default="DEBUG")
    
    log_file: str = Field(default="./logs/app.log")

    log_max_bytes: int = Field(default=5_000_000)

    log_backup_count: int = Field(default=3)


    # --- Multi-tenancy Settings ---
    allowed_tenants: list[str] = Field(
    default=["liver", "cardiology", "nephrology"],
    description="List of allowed tenant IDs for multi-tenancy support",
)


settings = Settings()