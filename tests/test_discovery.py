from pathlib import Path

from cloud_app_permission_scanner.config import ScanConfig
from cloud_app_permission_scanner.discovery import ClassFileFinder


def make_tree(root: Path, rel_paths: list[str]) -> None:
    for rel in rel_paths:
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(b"\xca\xfe\xba\xbe")


def found(root: Path, **kwargs) -> set[str]:
    finder = ClassFileFinder(ScanConfig(root=root, **kwargs))
    return {p.relative_to(root).as_posix() for p in finder.find()}


def test_finds_only_class_files(tmp_path: Path) -> None:
    make_tree(tmp_path, ["a/A.class", "a/B.java", "b/c/C.class", "README.md"])
    assert found(tmp_path) == {"a/A.class", "b/c/C.class"}


def test_exclude_regex(tmp_path: Path) -> None:
    make_tree(tmp_path, ["main/A.class", "test/B.class"])
    assert found(tmp_path, exclude_regex=r"/test/") == {"main/A.class"}


def test_include_path_substring(tmp_path: Path) -> None:
    make_tree(tmp_path, ["target/classes/A.class", "other/B.class"])
    assert found(tmp_path, include_path_substr="target/classes") == {
        "target/classes/A.class"
    }


def test_package_substring(tmp_path: Path) -> None:
    make_tree(tmp_path, ["com/acme/A.class", "org/other/B.class"])
    assert found(tmp_path, package_substr="com/acme") == {"com/acme/A.class"}


def test_none_filters_match_everything(tmp_path: Path) -> None:
    make_tree(tmp_path, ["A.class", "x/B.class"])
    assert found(tmp_path, include_path_substr=None, package_substr=None) == {
        "A.class",
        "x/B.class",
    }


def test_contains_sdk_reference(tmp_path: Path) -> None:
    hit = tmp_path / "Hit.class"
    miss = tmp_path / "Miss.class"
    hit.write_bytes(b"\x00software/amazon/awssdk/services/s3/S3Client\x00")
    miss.write_bytes(b"\x00java/lang/String\x00")
    assert ClassFileFinder.contains_sdk_reference(hit)
    assert not ClassFileFinder.contains_sdk_reference(miss)
    assert not ClassFileFinder.contains_sdk_reference(tmp_path / "Missing.class")
