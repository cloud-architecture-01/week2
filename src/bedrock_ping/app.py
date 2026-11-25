"""GET /bedrock-ping: Lambda에서 Bedrock Claude 모델을 호출할 수 있는지 확인합니다.

사용자 입력을 받지 않고 고정된 질문 하나만 보내서, 외부에서 호출해도 비용이 크게 늘지 않게 했습니다.
"""

import json
import os
import time

import boto3
from botocore.exceptions import ClientError

MODEL_ID = os.environ.get("MODEL_ID", "")
PROMPT = "충남대학교 컴퓨터융합학부 학생을 돕는 챗봇이라고 한 문장으로 자기소개해 주세요."

_client = None


def _bedrock():
    global _client
    if _client is None:
        _client = boto3.client("bedrock-runtime")
    return _client


def _response(status, body):
    return {
        "statusCode": status,
        "headers": {"Content-Type": "application/json; charset=utf-8"},
        "body": json.dumps(body, ensure_ascii=False),
    }


def handler(event, context):
    started = time.perf_counter()
    try:
        result = _bedrock().converse(
            modelId=MODEL_ID,
            messages=[{"role": "user", "content": [{"text": PROMPT}]}],
            inferenceConfig={"maxTokens": 100, "temperature": 0},
        )
    except ClientError as err:
        error = err.response.get("Error", {})
        print(json.dumps({"event": "bedrock_error", "code": error.get("Code"), "model": MODEL_ID}))
        return _response(502, {
            "status": "error",
            "model": MODEL_ID,
            "error_code": error.get("Code"),
            "message": error.get("Message"),
        })

    reply = "".join(
        part.get("text", "") for part in result["output"]["message"]["content"]
    )
    latency_ms = round((time.perf_counter() - started) * 1000)
    usage = result.get("usage", {})
    print(json.dumps({"event": "bedrock_ok", "model": MODEL_ID, "latency_ms": latency_ms, "usage": usage}))
    return _response(200, {
        "status": "ok",
        "model": MODEL_ID,
        "prompt": PROMPT,
        "reply": reply,
        "latency_ms": latency_ms,
        "usage": usage,
    })
