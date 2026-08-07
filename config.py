import os
from pathlib import Path

class BaseConfig:
    """
    Base configuration shared across all environments.
    """
    
    PROJECT_ROOT = Path(__file__).resolve().parent

    DATABASE_PATH = PROJECT_ROOT / "market_data.db"


class DevelopmentConfig(BaseConfig):
    """
    Development environment configuration.
    """
    DEBUG = True
    HOST = "127.0.0.1"
    PORT = 5000
    LOG_LEVEL = "DEBUG"
    TESTING = False
    RATELIMIT_ENABLED = True

class TestConfig(DevelopmentConfig):
    TESTING = True
    RATELIMIT_ENABLED = False



class ProductionConfig(BaseConfig):
    """
    Production environment configuration.
    """
    DEBUG = False
    HOST = "0.0.0.0"
    PORT = int(os.environ.get("PORT", 5000))
    LOG_LEVEL = "INFO"
    TESTING = False
    RATELIMIT_ENABLED = True