import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    ENVIRONMENT: str = os.environ.get("ENVIRONMENT", "development")
    FINAL_FLAG: str = os.environ.get("FINAL_FLAG", "KCTF{11TH_D4Y_UNL0CK3D}")
    SUPABASE_URL: str = os.environ.get("SUPABASE_URL", "http://localhost:8000")
    SUPABASE_KEY: str = os.environ.get("SUPABASE_KEY", "dummy")
    TOGETHER_API_KEY: str = os.environ.get("TOGETHER_API_KEY", "dummy")
    MODEL_NAME: str = "meta-llama/Llama-3-8b-chat-hf" # Using closest available for Qwen3-8B

settings = Settings()


