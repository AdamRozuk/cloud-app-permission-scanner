"""
cloud_app_permission_scanner
====================

Scan compiled .class files for AWS SDK v2 service-client method references
and generate an IAM permissions policy JSON.

Public API::

    from cloud_app_permission_scanner import ScanConfig, run

    config = ScanConfig(root=Path("my-repo"), print_calls=True)
    exit_code = run(config)
"""

from cloud_app_permission_scanner.config import ScanConfig
from cloud_app_permission_scanner.models import ScanResult, ServiceCall
from cloud_app_permission_scanner.runner import run

__all__ = ["ScanConfig", "ScanResult", "ServiceCall", "run"]
