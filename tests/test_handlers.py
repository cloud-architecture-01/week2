"""배포 전에 로컬에서 handler 동작을 확인하는 테스트입니다. 실제 AWS를 호출하지 않습니다."""

import importlib.util
import json
from pathlib import Path

from botocore.exceptions import ClientError

ROOT = Path(__file__).resolve().parents[1]


def load(name, rel):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_health_returns_ok():
    health = load("health_app", "src/health/app.py")
    res = health.handler({}, None)
    assert res["statusCode"] == 200
    body = json.loads(res["body"])
    assert body["status"] == "ok"
    assert body["service"] == "cnu-cc-guide"


class FakeBedrock:
    def __init__(self, fail=False):
        self.fail = fail

    def converse(self, **kwargs):
        if self.fail:
            raise ClientError(
                {"Error": {"Code": "AccessDeniedException", "Message": "no access"}}, "Converse"
            )
        return {
            "output": {"message": {"content": [{"text": "안녕하세요, 컴융 길잡이입니다."}]}},
            "usage": {"inputTokens": 30, "outputTokens": 12, "totalTokens": 42},
        }


def test_bedrock_ping_ok(monkeypatch):
    ping = load("ping_app", "src/bedrock_ping/app.py")
    monkeypatch.setattr(ping, "_bedrock", lambda: FakeBedrock())
    res = ping.handler({}, None)
    body = json.loads(res["body"])
    assert res["statusCode"] == 200
    assert body["reply"].startswith("안녕하세요")


def test_bedrock_ping_error(monkeypatch):
    ping = load("ping_app_err", "src/bedrock_ping/app.py")
    monkeypatch.setattr(ping, "_bedrock", lambda: FakeBedrock(fail=True))
    res = ping.handler({}, None)
    body = json.loads(res["body"])
    assert res["statusCode"] == 502
    assert body["error_code"] == "AccessDeniedException"
