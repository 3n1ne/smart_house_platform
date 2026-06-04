import os


def _env_bool(name, default=False):
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


class BaseConfig:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    SENSITIVE_DATA_KEY = os.getenv("SENSITIVE_DATA_KEY")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-jwt-secret-key")
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URI",
        "mysql+pymysql://root:lizhehan123456@127.0.0.1:3306/rent_house",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JSON_AS_ASCII = False
    UPLOAD_FOLDER = os.getenv(
        "UPLOAD_FOLDER",
        os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads"),
    )
    MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", 20 * 1024 * 1024))
    AUTO_CREATE_DB = _env_bool("AUTO_CREATE_DB", True)
    MFA_REQUIRED = _env_bool("MFA_REQUIRED", False)
    MFA_CODE_TTL_SECONDS = int(os.getenv("MFA_CODE_TTL_SECONDS", 300))
    MFA_CODE_VISIBLE = _env_bool("MFA_CODE_VISIBLE", True)


class DevelopmentConfig(BaseConfig):
    DEBUG = True


class TestingConfig(BaseConfig):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.getenv("TEST_DATABASE_URI", "sqlite:///:memory:")
    JWT_SECRET_KEY = "test-jwt-secret-key-for-rent-house-suite"
    MFA_CODE_VISIBLE = True
    UPLOAD_FOLDER = os.getenv(
        "TEST_UPLOAD_FOLDER",
        os.path.join(os.path.dirname(os.path.dirname(__file__)), "test_uploads"),
    )


class ProductionConfig(BaseConfig):
    DEBUG = False
    AUTO_CREATE_DB = _env_bool("AUTO_CREATE_DB", False)
    MFA_CODE_VISIBLE = _env_bool("MFA_CODE_VISIBLE", False)


config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}
