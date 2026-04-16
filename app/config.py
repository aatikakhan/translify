from dataclasses import dataclass
import os

from dotenv import load_dotenv

load_dotenv()


def _to_bool(value: str, default: bool = False) -> bool:
    if value is None:
        return default
    return value.lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    app_name: str = os.getenv("APP_NAME", "Translify")
    app_env: str = os.getenv("APP_ENV", "development")
    app_debug: bool = _to_bool(os.getenv("APP_DEBUG"), default=False)
    secret_key: str = os.getenv("SECRET_KEY", "dev-secret-change-me")

    database_url: str = os.getenv(
        "DATABASE_URL", "sqlite:///./translify_dev.db"
    )

    aws_region: str = os.getenv("AWS_REGION", "ap-south-1")
    aws_s3_bucket: str = os.getenv("AWS_S3_BUCKET", "")
    aws_access_key_id: str = os.getenv("AWS_ACCESS_KEY_ID", "")
    aws_secret_access_key: str = os.getenv("AWS_SECRET_ACCESS_KEY", "")

    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

    use_local_storage: bool = _to_bool(
        os.getenv("USE_LOCAL_STORAGE"), default=True
    )
    local_storage_dir: str = os.getenv("LOCAL_STORAGE_DIR", "./local_storage")


settings = Settings()
