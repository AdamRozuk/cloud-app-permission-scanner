import pytest

from cloud_app_permission_scanner.constants import (
    iam_prefix,
    sanitize_sid,
    to_pascal,
    unique_sid,
)


@pytest.mark.parametrize(
    ("name", "expected"),
    [("getObject", "GetObject"), ("x", "X"), ("", ""), ("Already", "Already")],
)
def test_to_pascal(name: str, expected: str) -> None:
    assert to_pascal(name) == expected


def test_sanitize_sid_strips_non_alphanumerics() -> None:
    assert sanitize_sid("cloudtrail-data Access!") == "cloudtraildataAccess"


def test_sanitize_sid_falls_back_when_empty() -> None:
    assert sanitize_sid("---") == "Stmt"


def test_unique_sid_adds_numeric_suffix() -> None:
    used: set[str] = set()
    assert unique_sid("s3Access", used) == "s3Access"
    assert unique_sid("s3Access", used) == "s3Access2"
    assert unique_sid("s3-Access", used) == "s3Access3"
    assert used == {"s3Access", "s3Access2", "s3Access3"}


@pytest.mark.parametrize(
    ("service", "prefix"),
    [
        ("cloudwatchlogs", "logs"),
        ("cloudtraildata", "cloudtrail-data"),
        ("dynamodb", "dynamodb"),
        ("s3", "s3"),
    ],
)
def test_iam_prefix(service: str, prefix: str) -> None:
    assert iam_prefix(service) == prefix
