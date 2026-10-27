"""Shared fixtures: compile the Java samples under ``tests/fixtures/java``."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest

JAVA_FIXTURES = Path(__file__).parent / "fixtures" / "java"

requires_jdk = pytest.mark.skipif(
    shutil.which("javac") is None or shutil.which("javap") is None,
    reason="javac/javap not on PATH",
)


def _javac(sources: list[Path], out_dir: Path, classpath: Path | None = None) -> None:
    cmd = ["javac", "-d", str(out_dir)]
    if classpath is not None:
        cmd += ["-cp", str(classpath)]
    cmd += [str(s) for s in sources]
    subprocess.run(cmd, check=True, capture_output=True)


@pytest.fixture(scope="session")
def compiled_app(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Compile the SDK stubs and sample app; return the app's classes directory."""
    if shutil.which("javac") is None:
        pytest.skip("javac not on PATH")
    base = tmp_path_factory.mktemp("java")
    stubs_out = base / "stubs"
    app_out = base / "app"
    _javac(sorted((JAVA_FIXTURES / "stubs").rglob("*.java")), stubs_out)
    _javac(sorted((JAVA_FIXTURES / "app").rglob("*.java")), app_out, stubs_out)
    return app_out
