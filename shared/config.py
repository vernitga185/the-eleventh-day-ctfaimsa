import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    ENVIRONMENT: str = os.environ.get("ENVIRONMENT", "development")
    FINAL_FLAG: str = os.environ.get("FINAL_FLAG", "FLAG{3l3v3nth_d4y_kuru_c0unc1l_s34l_br0k3n_9f8b2}")
    SUPABASE_URL: str = os.environ.get("SUPABASE_URL", "http://localhost:8000")
    SUPABASE_KEY: str = os.environ.get("SUPABASE_KEY", "dummy")
    TOGETHER_API_KEY: str = os.environ.get("TOGETHER_API_KEY", "dummy")
    MODEL_NAME: str = "meta-llama/Llama-3-8b-chat-hf" # Using closest available for Qwen3-8B

settings = Settings()


