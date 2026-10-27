import subprocess

import pytest

from cloud_app_permission_scanner.extractor import JavapExtractor
from cloud_app_permission_scanner.models import ServiceCall

JAVAP_SAMPLE = """\
Constant pool:
   #7 = InterfaceMethodref #8.#9   // software/amazon/awssdk/services/s3/S3Client.create:()Lsoftware/amazon/awssdk/services/s3/S3Client;
   #8 = Class              #10     // software/amazon/awssdk/services/s3/S3Client
  #21 = InterfaceMethodref #8.#22  // software/amazon/awssdk/services/s3/S3Client.getObject:(Ljava/lang/String;)Ljava/lang/String;
  #23 = InterfaceMethodref #8.#24  // software/amazon/awssdk/services/s3/S3Client.close:()V
  #25 = Methodref          #26.#27 // software/amazon/awssdk/services/s3/model/GetObjectRequest.builder:()Lsoftware/amazon/awssdk/services/s3/model/GetObjectRequest$Builder;
  #30 = InterfaceMethodref #31.#32 // software/amazon/awssdk/services/cloudwatchlogs/CloudWatchLogsClient.putLogEvents:(Ljava/lang/String;)V
  #40 = Methodref          #41.#42 // java/lang/String.toUpperCase:()Ljava/lang/String;
         5: invokeinterface #21,  2 // InterfaceMethod software/amazon/awssdk/services/s3/S3Client.getObject:(Ljava/lang/String;)Ljava/lang/String;
"""


def test_extract_calls_finds_client_operations() -> None:
    calls = JavapExtractor.extract_calls(JAVAP_SAMPLE)
    assert calls == {
        ServiceCall("s3", "S3Client", "getObject"),
        ServiceCall("cloudwatchlogs", "CloudWatchLogsClient", "putLogEvents"),
    }


def test_extract_calls_empty_input() -> None:
    assert JavapExtractor.extract_calls("") == set()


def test_disassemble_raises_when_javap_missing(monkeypatch, tmp_path) -> None:
    def fake_run(*args, **kwargs):
        raise FileNotFoundError("javap")

    monkeypatch.setattr(subprocess, "run", fake_run)
    with pytest.raises(RuntimeError, match="javap not found"):
        JavapExtractor.disassemble(tmp_path / "A.class")


def test_disassemble_returns_empty_on_os_error(monkeypatch, tmp_path) -> None:
    def fake_run(*args, **kwargs):
        raise PermissionError("denied")

    monkeypatch.setattr(subprocess, "run", fake_run)
    assert JavapExtractor.disassemble(tmp_path / "A.class") == ""
