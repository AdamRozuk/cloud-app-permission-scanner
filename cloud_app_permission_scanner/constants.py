"""IAM/SDK mapping constants and pure helper functions."""

from __future__ import annotations

import re

# ── SDK service key → IAM prefix (only exceptions; everything else maps 1:1) ──

IAM_PREFIX_OVERRIDES: dict[str, str] = {
    "cloudwatchlogs": "logs",
    "cloudtraildata": "cloudtrail-data",
}

# ── S3 quirks ──

S3_BUCKET_OPS: frozenset[str] = frozenset({"listObjects", "listObjectsV2"})

S3_KNOWN_ACTIONS: dict[str, str] = {
    "listObjects": "s3:ListBucket",
    "listObjectsV2": "s3:ListBucket",
    "getObject": "s3:GetObject",
    "putObject": "s3:PutObject",
}

# ── SDK client helper methods that are not real service operations ──

IGNORED_OPERATIONS: frozenset[str] = frozenset(
    {"close", "builder", "build", "create", "getClient", "client", "serviceClient"}
)

# ── Compiled regexes for javap constant-pool parsing ──

CALLEE_LINE_RE = re.compile(r"//\s*(software/amazon/awssdk/services/.*)$")
CALLEE_PARSE_RE = re.compile(
    r"^software/amazon/awssdk/services/([^/]+)/([^.]+Client)\.([^:]+):"
)

AWS_SDK_NEEDLE = b"software/amazon/awssdk/services/"

# ── Pure helpers ──


def to_pascal(name: str) -> str:
    """Convert a camelCase SDK operation name to PascalCase for IAM actions."""
    return name[:1].upper() + name[1:] if name else name


def sanitize_sid(raw: str) -> str:
    """Strip non-alphanumeric characters (IAM Sid requirement)."""
    cleaned = re.sub(r"[^A-Za-z0-9]", "", raw)
    return cleaned or "Stmt"


def unique_sid(base: str, used: set[str]) -> str:
    """Return *base* (sanitized) with a numeric suffix if already taken."""
    base = sanitize_sid(base)
    if base not in used:
        used.add(base)
        return base
    for i in range(2, 10_000):
        candidate = f"{base}{i}"
        if candidate not in used:
            used.add(candidate)
            return candidate
    raise RuntimeError(f"Could not generate unique SID for base '{base}'")


def iam_prefix(service_key: str) -> str:
    """Map an SDK service key to its IAM action prefix."""
    return IAM_PREFIX_OVERRIDES.get(service_key, service_key)
