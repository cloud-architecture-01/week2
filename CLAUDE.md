# 컴융 길잡이 (cnu-cc-guide)

충남대학교 컴퓨터융합학부 학생에게 학사 공지, 장학금, 졸업 요건을 근거 문서와 함께 안내하는 RAG 챗봇입니다.

## 구성
- 리전: ap-northeast-2 (서울). 모든 리소스 이름은 cnu-cc-guide 로 시작합니다.
- 백엔드: API Gateway (REST) + Lambda (Python 3.13, arm64), AWS SAM으로 배포 (template.yaml)
- 저장소: S3 문서 버킷 cnu-cc-guide-docs-<계정 ID>, S3 Vectors cnu-cc-guide-vectors / cnu-cc-guide-index (1024차원, cosine), DynamoDB cnu-cc-guide-chat
- 모델: Amazon Bedrock. 임베딩은 Titan Text Embeddings V2, 생성은 Claude (inference profile ID는 template.yaml의 ModelId)

## 자주 쓰는 명령
- 테스트: `python -m pytest -q`
- 빌드와 배포: `sam build && sam deploy`
- 삭제: `sam delete --stack-name cnu-cc-guide-dev --region ap-northeast-2`

## 규칙
- access key, API key 같은 비밀 값은 코드와 커밋에 넣지 않습니다.
- Lambda IAM 권한은 필요한 action과 resource만 template.yaml에 적습니다.
- 커밋 메시지는 `feat:`, `fix:`, `docs:`, `chore:`, `test:` 로 시작합니다.
