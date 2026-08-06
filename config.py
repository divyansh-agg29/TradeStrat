import os

class BaseConfig:
    """
    Base configuration shared across all environments.
    """
    DATABASE_PATH = "data/market_data.db"

\
class DevelopmentConfig(BaseConfig):
    """
    Development environment configuration.
    """
    DEBUG = True
    HOST = "127.0.0.1"
    PORT = 5000

class ProductionConfig(BaseConfig):
    """
    Production environment configuration.
    """
    DEBUG = False
    HOST = "0.0.0.0"
    PORT = int(os.environ.get("PORT", 5000))