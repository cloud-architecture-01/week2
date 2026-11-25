"""GET /health: Lambda와 API Gateway가 연결되어 있는지 확인합니다."""

import json
import os
from datetime import datetime, timezone


def handler(event, context):
    body = {
        "status": "ok",
        "service": "cnu-cc-guide",
        "stage": os.environ.get("STAGE", "dev"),
        "region": os.environ.get("AWS_REGION", "unknown"),
        "time": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json; charset=utf-8"},
        "body": json.dumps(body, ensure_ascii=False),
    }
