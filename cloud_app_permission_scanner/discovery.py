"""File discovery — walk the directory tree and filter .class files."""

from __future__ import annotations

import os
import re
from pathlib import Path

from cloud_app_permission_scanner.config import ScanConfig
from cloud_app_permission_scanner.constants import AWS_SDK_NEEDLE


class ClassFileFinder:
    """Walks a directory tree and yields matching ``.class`` files."""

    def __init__(self, config: ScanConfig) -> None:
        self._root = config.root
        self._include_substr = config.include_path_substr
        self._package_substr = config.package_substr
        self._exclude_re = (
            re.compile(config.exclude_regex) if config.exclude_regex else None
        )

    def find(self) -> list[Path]:
        """Return all ``.class`` files matching the configured filters."""
        results: list[Path] = []
        for dirpath, _, filenames in os.walk(self._root):
            for fn in filenames:
                if not fn.endswith(".class"):
                    continue
                full = os.path.join(dirpath, fn)
                if self._exclude_re and self._exclude_re.search(full):
                    continue
                if self._include_substr and self._include_substr not in full:
                    continue
                if self._package_substr and self._package_substr not in full:
                    continue
                results.append(Path(full))
        return results

    @staticmethod
    def contains_sdk_reference(path: Path) -> bool:
        """Fast binary check: does the classfile mention the SDK services prefix?"""
        try:
            return AWS_SDK_NEEDLE in path.read_bytes()
        except OSError:
            return False
