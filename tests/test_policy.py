from cloud_app_permission_scanner.models import ServiceCall
from cloud_app_permission_scanner.policy import IAMPolicyBuilder


def build(*calls: ServiceCall) -> dict:
    return IAMPolicyBuilder().build(set(calls))


def test_empty_calls_give_empty_policy() -> None:
    assert build() == {"Version": "2012-10-17", "Statement": []}


def test_generic_actions_grouped_and_sorted_by_prefix() -> None:
    policy = build(
        ServiceCall("sqs", "SqsClient", "sendMessage"),
        ServiceCall("dynamodb", "DynamoDbClient", "putItem"),
        ServiceCall("dynamodb", "DynamoDbClient", "getItem"),
    )
    assert policy["Statement"] == [
        {
            "Sid": "dynamodbAccess",
            "Effect": "Allow",
            "Action": ["dynamodb:GetItem", "dynamodb:PutItem"],
            "Resource": "*",
        },
        {
            "Sid": "sqsAccess",
            "Effect": "Allow",
            "Action": ["sqs:SendMessage"],
            "Resource": "*",
        },
    ]


def test_iam_prefix_override_applied() -> None:
    policy = build(
        ServiceCall("cloudwatchlogs", "CloudWatchLogsClient", "putLogEvents"),
    )
    (stmt,) = policy["Statement"]
    assert stmt["Sid"] == "logsAccess"
    assert stmt["Action"] == ["logs:PutLogEvents"]


def test_s3_split_into_bucket_and_object_statements() -> None:
    policy = build(
        ServiceCall("s3", "S3Client", "listObjectsV2"),
        ServiceCall("s3", "S3Client", "listObjects"),
        ServiceCall("s3", "S3Client", "getObject"),
        ServiceCall("s3", "S3Client", "deleteObject"),
    )
    assert policy["Statement"] == [
        {
            "Sid": "S3BucketAccess",
            "Effect": "Allow",
            "Action": ["s3:ListBucket"],
            "Resource": ["arn:aws:s3:::*"],
        },
        {
            "Sid": "S3ObjectAccess",
            "Effect": "Allow",
            "Action": ["s3:DeleteObject", "s3:GetObject"],
            "Resource": ["arn:aws:s3:::*/*"],
        },
    ]


def test_s3_statements_follow_generic_statements() -> None:
    policy = build(
        ServiceCall("s3", "S3Client", "getObject"),
        ServiceCall("sqs", "SqsClient", "sendMessage"),
    )
    assert [s["Sid"] for s in policy["Statement"]] == ["sqsAccess", "S3ObjectAccess"]
