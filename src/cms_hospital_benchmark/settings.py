"""Runtime configuration."""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Environment-driven file and HTTP settings."""

    model_config = SettingsConfigDict(env_prefix="CMS_", env_file=".env", extra="ignore")

    data_dir: Path = Path("data")
    warehouse_path: Path = Path("warehouse/cms_hospital.duckdb")
    http_timeout_seconds: float = 120.0
    page_size: int = 5000

    @property
    def raw_dir(self) -> Path:
        return self.data_dir / "raw"

    @property
    def staged_dir(self) -> Path:
        return self.data_dir / "staged"

    @property
    def manifest_dir(self) -> Path:
        return self.data_dir / "manifests"

    def ensure_directories(self) -> None:
        for path in (self.raw_dir, self.staged_dir, self.manifest_dir, self.warehouse_path.parent):
            path.mkdir(parents=True, exist_ok=True)
