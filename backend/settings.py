"""
Global settings for Grace Backend
"""
import os

class Settings:
    # Feature Flags
    SELF_HEAL_EXECUTE = os.getenv("SELF_HEAL_EXECUTE", "True").lower() == "true"
    ENABLE_CLI_VERIFY = os.getenv("ENABLE_CLI_VERIFY", "False").lower() == "true"
    
    # Service URLs
    SELF_HEAL_BASE_URL = os.getenv("SELF_HEAL_BASE_URL", "http://localhost:8000")
    
    # Timeouts
    SELF_HEAL_RUN_TIMEOUT_MIN = int(os.getenv("SELF_HEAL_RUN_TIMEOUT_MIN", 10))

settings = Settings()
