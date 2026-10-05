from pathlib import Path

from cms_hospital_benchmark.settings import Settings


def test_settings_build_expected_subdirectories(tmp_path: Path):
    settings = Settings(data_dir=tmp_path / "cms", warehouse_path=tmp_path / "warehouse.duckdb")
    settings.ensure_directories()
    assert settings.raw_dir.is_dir()
    assert settings.staged_dir.is_dir()
    assert settings.manifest_dir.is_dir()
