"""Runner — pipeline orchestration and CLI entry point."""

from __future__ import annotations

import json
import logging
import sys

from cloud_app_permission_scanner.config import ScanConfig
from cloud_app_permission_scanner.policy import IAMPolicyBuilder
from cloud_app_permission_scanner.scanner import ClassScanner

logger = logging.getLogger(__name__)


def _write_policy(policy: dict, config: ScanConfig) -> None:
    """Serialize *policy* as JSON, creating parent directories as needed."""
    config.output.parent.mkdir(parents=True, exist_ok=True)
    config.output.write_text(json.dumps(policy, indent=2) + "\n", encoding="utf-8")


def run(config: ScanConfig) -> int:
    """Execute the full scan-and-generate pipeline. Returns an exit code."""
    scanner = ClassScanner(config)
    result = scanner.scan()

    if result.candidates_count == 0:
        return 2

    if result.scanned_count == 0:
        return 0

    policy = IAMPolicyBuilder().build(result.calls)
    _write_policy(policy, config)

    if config.print_calls:
        for call in sorted(result.calls):
            print(f"{call.service}\t{call.client}\t{call.operation}")

    logger.info(
        "Wrote %s from %d discovered AWS SDK v2 service operations "
        "(scanned %d/%d classfiles; %d failures).",
        config.output,
        len(result.calls),
        result.scanned_count,
        result.candidates_count,
        result.failure_count,
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(levelname)s: %(message)s",
        stream=sys.stderr,
    )
    config = ScanConfig.from_cli(argv)
    if not config.debug:
        logging.getLogger("cloud_app_permission_scanner").setLevel(logging.INFO)
    return run(config)
