"""
Configuration settings for prostate MRI segmentation tool
"""

import os
from pathlib import Path

class Config:
    """Base configuration class"""

    # Application settings
    APP_NAME = "Prostate MRI Segmentation Tool"
    VERSION = "1.0.0"

    # Database settings
    DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///segmentation.db')

    # Storage settings
    STORAGE_PATH = Path(os.environ.get('STORAGE_PATH', './data'))
    USER_DATA_PATH = STORAGE_PATH / 'user_data'
    SEGMENTATION_DATA_PATH = STORAGE_PATH / 'segmentations'
    DICOM_DATA_PATH = STORAGE_PATH / 'dicom'

    # AI Model settings
    AI_MODEL_PATH = Path(os.environ.get('AI_MODEL_PATH', './models'))
    DEFAULT_AI_MODEL = "unet_prostate"

    # Web interface settings
    WEB_HOST = os.environ.get('WEB_HOST', '0.0.0.0')
    WEB_PORT = int(os.environ.get('WEB_PORT', 5000))
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-12345')

    # Multi-user settings
    MULTI_USER_ENABLED = os.environ.get('MULTI_USER_ENABLED', 'true').lower() == 'true'
    SESSION_TIMEOUT = int(os.environ.get('SESSION_TIMEOUT', 3600))  # 1 hour

    # DICOM settings
    DICOM_TIMEOUT = int(os.environ.get('DICOM_TIMEOUT', 30))
    DICOM_LOAD_THREADS = int(os.environ.get('DICOM_LOAD_THREADS', 4))

    # Performance settings
    MAX_SEGMENTATION_THREADS = int(os.environ.get('MAX_SEGMENTATION_THREADS', 4))
    CACHE_SIZE = int(os.environ.get('CACHE_SIZE', 100))

    # Logging settings
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = os.environ.get('LOG_FILE', './logs/app.log')

    # Feature flags
    FEATURE_AI_PRESEGMENTATION = os.environ.get('FEATURE_AI_PRESEGMENTATION', 'true').lower() == 'true'
    FEATURE_MULTI_SERIES = os.environ.get('FEATURE_MULTI_SERIES', 'true').lower() == 'true'
    FEATURE_REALTIME_COLLABORATION = os.environ.get('FEATURE_REALTIME_COLLABORATION', 'true').lower() == 'true'

    # Default values for segmentation tools
    DEFAULT_BRUSH_SIZE = 5
    DEFAULT_THRESHOLD = 128
    DEFAULT_WATERSHED_PARAMS = {
        'connectivity': 8,
        'markers': None
    }

    # UI settings
    DEFAULT_WINDOW_SIZE = (1200, 800)
    DEFAULT_TOOLBAR_SIZE = (200, 800)

    @classmethod
    def init_directories(cls):
        """Initialize required directories"""
        cls.STORAGE_PATH.mkdir(exist_ok=True)
        cls.USER_DATA_PATH.mkdir(exist_ok=True)
        cls.SEGMENTATION_DATA_PATH.mkdir(exist_ok=True)
        cls.DICOM_DATA_PATH.mkdir(exist_ok=True)
        cls.AI_MODEL_PATH.mkdir(exist_ok=True)

        # Create logs directory
        log_dir = Path(cls.LOG_FILE).parent
        log_dir.mkdir(exist_ok=True)

# Create directories on import
Config.init_directories()

# Environment-specific configurations
class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    LOG_LEVEL = 'DEBUG'

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    LOG_LEVEL = 'WARNING'

class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = True
    TESTING = True
    DATABASE_URL = 'sqlite:///:memory:'

# Configuration factory
def get_config(config_name=None):
    """Get configuration based on environment"""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')

    configs = {
        'development': DevelopmentConfig,
        'production': ProductionConfig,
        'testing': TestingConfig
    }

    return configs.get(config_name, DevelopmentConfig)