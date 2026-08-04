"""Javap extraction — disassemble class files and parse AWS SDK service calls."""

from __future__ import annotations

import logging
import subprocess
from pathlib import Path

from cloud_app_permission_scanner.constants import (
    CALLEE_LINE_RE,
    CALLEE_PARSE_RE,
    IGNORED_OPERATIONS,
)
from cloud_app_permission_scanner.models import ServiceCall

logger = logging.getLogger(__name__)


class JavapExtractor:
    """Runs ``javap -verbose`` and extracts AWS SDK service calls."""

    @staticmethod
    def disassemble(classfile: Path) -> str:
        """Return javap constant-pool output for *classfile*."""
        try:
            proc = subprocess.run(
                ["javap", "-verbose", str(classfile)],
                capture_output=True,
                text=True,
                check=False,
            )
            return proc.stdout or ""
        except FileNotFoundError:
            raise RuntimeError(
                "javap not found. Ensure a JDK is installed and javap is on PATH."
            )
        except OSError as exc:
            logger.warning("javap failed for %s: %s", classfile, exc)
            return ""

    @staticmethod
    def extract_calls(javap_output: str) -> set[ServiceCall]:
        """Parse javap output and return discovered ``ServiceCall`` instances."""
        calls: set[ServiceCall] = set()
        for line in javap_output.splitlines():
            if "software/amazon/awssdk/services/" not in line:
                continue
            match = CALLEE_LINE_RE.search(line)
            if not match:
                continue
            callee = match.group(1).strip()
            parsed = CALLEE_PARSE_RE.match(callee)
            if not parsed:
                continue
            service, client, operation = (
                parsed.group(1),
                parsed.group(2),
                parsed.group(3),
            )
            if operation in IGNORED_OPERATIONS:
                continue
            calls.add(ServiceCall(service, client, operation))
        return calls
