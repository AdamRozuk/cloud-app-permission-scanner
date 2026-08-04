"""Domain types shared across the package."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import NamedTuple


class ServiceCall(NamedTuple):
    """A single AWS SDK v2 service-client method reference."""

    service: str
    client: str
    operation: str


@dataclass
class ScanResult:
    """Aggregated results from scanning class files."""

    calls: set[ServiceCall] = field(default_factory=set)
    candidates_count: int = 0
    scanned_count: int = 0
    failure_count: int = 0
