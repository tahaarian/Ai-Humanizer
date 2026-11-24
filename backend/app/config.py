from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    # app
    secret_key: str = "change-me-in-production"
    public_url: str = "http://localhost:3000"      # what the browser sees (Next.js proxies /api and /auth)
    database_url: str = "sqlite:///./data/app.db"
    # auth
    google_client_id: str = ""
    google_client_secret: str = ""
    dev_login: bool = False                         # local testing without Google
    admin_emails: str = ""                          # comma separated
    allowed_email_domains: str = ""                 # empty = anyone
    # LLM provider (Ollama-compatible; point to Colab/GPU tunnel later)
    llm_url: str = "http://localhost:11434"
    llm_api_key: str = ""
    llm_model: str = "qwen2.5:14b-instruct"
    llm_timeout: int = 900
    # pipeline
    max_passes: int = 2
    candidates: int = 3
    target_score: float = 35
    max_words_per_job: int = 5000
    daily_word_limit: int = 15000
    worker_concurrency: int = 1
    # privacy
    result_retention_hours: int = 24

    @property
    def admins(self): return {e.strip().lower() for e in self.admin_emails.split(",") if e.strip()}
    @property
    def domains(self): return {d.strip().lower() for d in self.allowed_email_domains.split(",") if d.strip()}

@lru_cache
def get_settings() -> Settings: return Settings()
