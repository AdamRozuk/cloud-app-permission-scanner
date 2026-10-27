import re
from pathlib import Path
import pytest

from cloud_app_permission_scanner.config import ScanConfig
from cloud_app_permission_scanner.discovery import ClassFileFinder


def test_discovery_uses_only_regex_filters(tmp_path):
    root = tmp_path / "scan-root"
    keep_dir = root / "com" / "example" / "keep"
    keep_dir.mkdir(parents=True)
    skip_dir = root / "com" / "example" / "generated"
    skip_dir.mkdir(parents=True)

    keep_file = keep_dir / "Keep.class"
    keep_file.write_bytes(b"keep")
    skip_file = skip_dir / "Skip.class"
    skip_file.write_bytes(b"skip")
    another_keep = root / "com" / "example" / "other.class"
    another_keep.write_bytes(b"other")

    config = ScanConfig(
        root=root,
        include_re=r".*com/example/.*",
        exclude_re=r".*generated.*",
    )
    finder = ClassFileFinder(config)

    assert finder.is_eligible(root / "com" / "example" / "keep" / "Keep.class")
    assert not finder.is_eligible(root / "com" / "example" / "generated" / "Skip.class")
    # Also verify backward-compatible camelCase alias
    assert finder.isEligible(root / "com" / "example" / "keep" / "Keep.class")

    found = [path.name for path in finder.find()]

    assert found == ["Keep.class", "other.class"]


def test_discovery_no_filters_finds_all_class_files(tmp_path):
    root = tmp_path / "scan-root"
    pkg_dir = root / "com" / "example"
    pkg_dir.mkdir(parents=True)

    (pkg_dir / "One.class").write_bytes(b"one")
    (pkg_dir / "Two.class").write_bytes(b"two")
    (pkg_dir / "NotClass.txt").write_text("text")

    config = ScanConfig(root=root)
    finder = ClassFileFinder(config)

    found = [path.name for path in finder.find()]
    assert sorted(found) == ["One.class", "Two.class"]


def test_discovery_exclude_filter_only(tmp_path):
    root = tmp_path / "scan-root"
    pkg_dir = root / "com" / "example"
    pkg_dir.mkdir(parents=True)

    (pkg_dir / "Regular.class").write_bytes(b"regular")
    (pkg_dir / "TestIgnored.class").write_bytes(b"test")

    config = ScanConfig(root=root, exclude_re=r".*Test.*")
    finder = ClassFileFinder(config)

    found = [path.name for path in finder.find()]
    assert found == ["Regular.class"]


def test_discovery_accepts_compiled_pattern(tmp_path):
    root = tmp_path / "scan-root"
    pkg_dir = root / "com" / "example"
    pkg_dir.mkdir(parents=True)

    (pkg_dir / "App.class").write_bytes(b"app")
    (pkg_dir / "Mock.class").write_bytes(b"mock")

    config = ScanConfig(
        root=root,
        include_re=re.compile(r"App\.class$"),
    )
    finder = ClassFileFinder(config)

    found = [path.name for path in finder.find()]
    assert found == ["App.class"]


def test_invalid_regex_raises_argparse_error():
    with pytest.raises(SystemExit) as exc_info:
        ScanConfig.from_cli(["--include-re", "["])
    assert exc_info.value.code == 2

    with pytest.raises(SystemExit) as exc_info:
        ScanConfig.from_cli(["--exclude-re", "("])
    assert exc_info.value.code == 2
