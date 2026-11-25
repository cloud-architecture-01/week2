# 컴융 길잡이 (cnu-cc-guide)

충남대학교 컴퓨터융합학부 대학 생활 안내 RAG 챗봇입니다. 이 저장소는 2주차 환경 구성 단계로, 테스트 API 2개와 저장소 생성 script를 담고 있습니다.

| 경로 | 내용 |
| --- | --- |
| template.yaml | API Gateway, Lambda 2개, log group을 정의한 AWS SAM template |
| src/health/app.py | GET /health: Lambda 실행 확인 |
| src/bedrock_ping/app.py | GET /bedrock-ping: Bedrock Claude 호출 확인 |
| scripts/create_storage.sh | S3 문서 버킷, S3 Vectors, DynamoDB 생성 |
| tests/ | AWS 없이 handler를 확인하는 pytest |
| CLAUDE.md | Claude Code가 읽는 프로젝트 설명 |

## 준비물
- AWS CLI v2 (2.32.0 이상이면 `aws login` 사용 가능)
- AWS SAM CLI
- Python 3.13
- Git, GitHub 계정
- Claude Code

## 실행 순서
```bash
# 0. 자격 증명 (브라우저로 콘솔 로그인 후 임시 자격 증명을 받습니다)
aws login
aws sts get-caller-identity

# 1. 저장소 만들기 (처음 한 번)
bash scripts/create_storage.sh

# 2. 로컬 테스트
python -m pip install pytest boto3
python -m pytest -q

# 3. 서울 리전에서 쓸 수 있는 Claude inference profile 확인
aws bedrock list-inference-profiles --region ap-northeast-2 \
  --query "inferenceProfileSummaries[?contains(inferenceProfileId, 'claude')].inferenceProfileId"

# 4. 배포 (처음 한 번은 --guided 로 설정을 확인합니다)
sam build
sam deploy --guided   # 이후에는 sam deploy

# 5. 실행 확인 (Outputs에 나온 주소 사용)
curl https://<api-id>.execute-api.ap-northeast-2.amazonaws.com/dev/health
curl https://<api-id>.execute-api.ap-northeast-2.amazonaws.com/dev/bedrock-ping
```

`/bedrock-ping`이 AccessDeniedException을 돌려주면, Bedrock 콘솔의 Model catalog에서 Anthropic 모델을 골라 사용 사례 양식(FTU)을 먼저 제출하고 playground에서 한 번 호출해 봅니다. 3단계에서 나온 ID가 기본값과 다르면 `sam deploy --parameter-overrides ModelId=<ID>`로 바꿉니다.

## 정리
```bash
sam delete --stack-name cnu-cc-guide-dev --region ap-northeast-2
```
저장소(S3, S3 Vectors, DynamoDB)는 3주차에도 쓰므로 지우지 않습니다.
