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
        description="المسار اللي ChromaDB هيحفظ فيه البيانات",
    )
    collection_name: str = Field(
        default="liver_care_docs",
        description="اسم الـ collection في ChromaDB",
    )
    embedding_model: str = Field(
        default="paraphrase-multilingual-MiniLM-L12-v2",
        description="HuggingFace embedding model — بيدعم عربي وانجليزي",
    )
    chunk_size: int = Field(
        default=500,
        description="عدد الكلمات في كل chunk",
    )
    chunk_overlap: int = Field(
        default=50,
        description="عدد الكلمات المتداخلة بين الـ chunks",
    )
    retrieval_top_k: int = Field(
        default=3,
        description="عدد الـ chunks اللي هيتجابوا من الـ vector store",
    )
    upload_dir: str = Field(
        default="./uploads",
        description="المسار اللي الـ PDFs هتترفع فيه",
    )


settings = Settings()