from pathlib import Path

from cloud_app_permission_scanner.config import ScanConfig


def test_from_cli_defaults() -> None:
    config = ScanConfig.from_cli([])
    assert config.root == Path(".")
    assert config.include_path_substr == "/"
    assert config.package_substr == "/"
    assert config.exclude_regex is None
    assert config.output == Path("permissions-policy.json")
    assert config.jobs >= 1
    assert not config.print_calls
    assert not config.debug


def test_from_cli_parses_arguments() -> None:
    config = ScanConfig.from_cli(
        [
            "--root",
            "build",
            "--include-path-substr",
            "classes",
            "--exclude-regex",
            "Test",
            "--package-substr",
            "com/acme",
            "--jobs",
            "3",
            "--out",
            "out/policy.json",
            "--print-calls",
            "--debug",
        ]
    )
    assert config == ScanConfig(
        root=Path("build"),
        include_path_substr="classes",
        exclude_regex="Test",
        package_substr="com/acme",
        jobs=3,
        output=Path("out/policy.json"),
        print_calls=True,
        debug=True,
    )


def test_from_cli_empty_strings_disable_filters() -> None:
    config = ScanConfig.from_cli(["--include-path-substr", "", "--package-substr", ""])
    assert config.include_path_substr is None
    assert config.package_substr is None
