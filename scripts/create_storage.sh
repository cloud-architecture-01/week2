#!/usr/bin/env bash
# 2주차 저장소 3가지(S3 문서 버킷, S3 Vectors 벡터 버킷과 인덱스, DynamoDB 테이블)를 만듭니다.
# 실행 전: aws login (또는 aws configure) 으로 자격 증명을 준비합니다.
# 사용법: bash scripts/create_storage.sh
set -euo pipefail

REGION="ap-northeast-2"
ACCOUNT_ID="$(aws sts get-caller-identity --query Account --output text)"
DOCS_BUCKET="cnu-cc-guide-docs-${ACCOUNT_ID}"
VECTOR_BUCKET="cnu-cc-guide-vectors"
VECTOR_INDEX="cnu-cc-guide-index"
TABLE="cnu-cc-guide-chat"

echo "[1/3] S3 문서 버킷: ${DOCS_BUCKET}"
aws s3api create-bucket --bucket "${DOCS_BUCKET}" --region "${REGION}" \
  --create-bucket-configuration LocationConstraint="${REGION}"
aws s3api put-public-access-block --bucket "${DOCS_BUCKET}" \
  --public-access-block-configuration BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true
aws s3api put-bucket-versioning --bucket "${DOCS_BUCKET}" --versioning-configuration Status=Enabled
aws s3api put-object --bucket "${DOCS_BUCKET}" --key raw/ >/dev/null
aws s3api put-object --bucket "${DOCS_BUCKET}" --key processed/ >/dev/null

echo "[2/3] S3 Vectors: ${VECTOR_BUCKET}/${VECTOR_INDEX}"
aws s3vectors create-vector-bucket --vector-bucket-name "${VECTOR_BUCKET}" --region "${REGION}"
# Knowledge Base가 청크 본문을 AMAZON_BEDROCK_TEXT에 저장하므로 두 key는 반드시 non-filterable 이어야 합니다.
# 인덱스를 만든 뒤에는 바꿀 수 없습니다.
aws s3vectors create-index --region "${REGION}" \
  --vector-bucket-name "${VECTOR_BUCKET}" --index-name "${VECTOR_INDEX}" \
  --data-type float32 --dimension 1024 --distance-metric cosine \
  --metadata-configuration '{"nonFilterableMetadataKeys":["AMAZON_BEDROCK_TEXT","AMAZON_BEDROCK_METADATA"]}'

echo "[3/3] DynamoDB 테이블: ${TABLE}"
aws dynamodb create-table --region "${REGION}" --table-name "${TABLE}" \
  --attribute-definitions AttributeName=session_id,AttributeType=S AttributeName=created_at,AttributeType=S \
  --key-schema AttributeName=session_id,KeyType=HASH AttributeName=created_at,KeyType=RANGE \
  --billing-mode PAY_PER_REQUEST --tags Key=project,Value=cnu-cc-guide >/dev/null
aws dynamodb wait table-exists --region "${REGION}" --table-name "${TABLE}"
aws dynamodb update-time-to-live --region "${REGION}" --table-name "${TABLE}" \
  --time-to-live-specification Enabled=true,AttributeName=expires_at >/dev/null

echo "완료. 확인 명령:"
echo "  aws s3api get-bucket-versioning --bucket ${DOCS_BUCKET}"
echo "  aws s3vectors get-index --region ${REGION} --vector-bucket-name ${VECTOR_BUCKET} --index-name ${VECTOR_INDEX}"
echo "  aws dynamodb describe-time-to-live --region ${REGION} --table-name ${TABLE}"
