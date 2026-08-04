"""Scan configuration — immutable settings for a scanning run."""

from __future__ import annotations

import argparse
import os
from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class ScanConfig:
    """Immutable configuration for a scanning run."""

    root: Path = Path(".")
    include_path_substr: str | None = "/"
    exclude_regex: str | None = None
    package_substr: str | None = "/"
    jobs: int = field(default_factory=lambda: max(1, os.cpu_count() or 4))
    output: Path = Path("permissions-policy.json")
    print_calls: bool = False
    debug: bool = False

    @classmethod
    def from_cli(cls, argv: list[str] | None = None) -> ScanConfig:
        """Build configuration from command-line arguments."""
        ap = argparse.ArgumentParser(
            description=(
                "Scan compiled .class files for AWS SDK v2 service client calls "
                "and generate an IAM permissions policy JSON."
            )
        )
        ap.add_argument("--root", default=".", help="Root directory to scan.")
        ap.add_argument(
            "--include-path-substr",
            default="/",
            help="Only scan classfiles whose path contains this substring.",
        )
        ap.add_argument(
            "--exclude-regex",
            default=None,
            help="Regex for classfile paths to exclude.",
        )
        ap.add_argument(
            "--package-substr",
            default="/",
            help="Only scan classfiles under this package path substring.",
        )
        ap.add_argument(
            "--jobs",
            type=int,
            default=max(1, os.cpu_count() or 4),
            help="Parallel workers (threads).",
        )
        ap.add_argument(
            "--out", default="permissions-policy.json", help="Output policy file."
        )
        ap.add_argument(
            "--print-calls",
            action="store_true",
            help="Print discovered service/client/op list to stdout.",
        )
        ap.add_argument(
            "--debug", action="store_true", help="Print progress info."
        )
        args = ap.parse_args(argv)
        return cls(
            root=Path(args.root),
            include_path_substr=args.include_path_substr or None,
            exclude_regex=args.exclude_regex or None,
            package_substr=args.package_substr or None,
            jobs=args.jobs,
            output=Path(args.out),
            print_calls=args.print_calls,
            debug=args.debug,
        )
