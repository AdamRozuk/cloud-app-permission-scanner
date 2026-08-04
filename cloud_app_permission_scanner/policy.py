"""IAM policy builder — converts ServiceCall sets into IAM policy documents."""

from __future__ import annotations

from collections import defaultdict

from cloud_app_permission_scanner.constants import (
    S3_BUCKET_OPS,
    S3_KNOWN_ACTIONS,
    iam_prefix,
    to_pascal,
    unique_sid,
)
from cloud_app_permission_scanner.models import ServiceCall

_POLICY_VERSION = "2012-10-17"


class IAMPolicyBuilder:
    """Converts a set of ``ServiceCall`` instances into an IAM policy document."""

    def build(self, calls: set[ServiceCall]) -> dict:
        """Return a complete IAM policy dict from the given service calls."""
        actions_by_prefix, s3_bucket_actions, s3_object_actions = self._classify(calls)

        used_sids: set[str] = set()
        statements = _build_generic_statements(actions_by_prefix, used_sids)
        statements.extend(
            _build_s3_statements(s3_bucket_actions, s3_object_actions, used_sids)
        )

        return {"Version": _POLICY_VERSION, "Statement": statements}

    @staticmethod
    def _classify(
        calls: set[ServiceCall],
    ) -> tuple[dict[str, set[str]], set[str], set[str]]:
        """Partition calls into generic service actions and S3 bucket/object actions."""
        actions_by_prefix: dict[str, set[str]] = defaultdict(set)
        s3_bucket_actions: set[str] = set()
        s3_object_actions: set[str] = set()

        for call in calls:
            prefix = iam_prefix(call.service)

            if prefix == "s3":
                action = S3_KNOWN_ACTIONS.get(
                    call.operation, f"s3:{to_pascal(call.operation)}"
                )
                target = (
                    s3_bucket_actions
                    if call.operation in S3_BUCKET_OPS
                    else s3_object_actions
                )
                target.add(action)
            else:
                actions_by_prefix[prefix].add(
                    f"{prefix}:{to_pascal(call.operation)}"
                )

        return actions_by_prefix, s3_bucket_actions, s3_object_actions


# ── Statement builders (module-private) ──────────────


def _build_generic_statements(
    actions_by_prefix: dict[str, set[str]], used_sids: set[str]
) -> list[dict]:
    statements: list[dict] = []
    for prefix in sorted(actions_by_prefix):
        actions = sorted(actions_by_prefix[prefix])
        if not actions:
            continue
        statements.append(
            {
                "Sid": unique_sid(f"{prefix}Access", used_sids),
                "Effect": "Allow",
                "Action": actions,
                "Resource": "*",
            }
        )
    return statements


def _build_s3_statements(
    bucket_actions: set[str],
    object_actions: set[str],
    used_sids: set[str],
) -> list[dict]:
    statements: list[dict] = []
    if bucket_actions:
        statements.append(
            {
                "Sid": unique_sid("S3BucketAccess", used_sids),
                "Effect": "Allow",
                "Action": sorted(bucket_actions),
                "Resource": ["arn:aws:s3:::*"],
            }
        )
    if object_actions:
        statements.append(
            {
                "Sid": unique_sid("S3ObjectAccess", used_sids),
                "Effect": "Allow",
                "Action": sorted(object_actions),
                "Resource": ["arn:aws:s3:::*/*"],
            }
        )
    return statements
