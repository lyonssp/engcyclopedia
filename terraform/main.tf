provider "aws" {
  region = "us-east-1"
}

data "aws_caller_identity" "current" {}

resource "aws_s3_bucket" "scrape_data" {
  bucket = "engcyclopedia-scrape-data"
}

resource "aws_lambda_function" "index" {
  function_name    = "index"
  handler          = "lambda_function.lambda_handler"
  runtime          = "python3.8"
  filename         = "lambda_package.zip"
  source_code_hash = filebase64sha256("lambda_package.zip")

  role = aws_iam_role.lambda_exec_role.arn

  timeout = 60

  environment {
    variables = {
      BUCKET_NAME     = aws_s3_bucket.scrape_data.bucket
      SEARCH_ENDPOINT = "https://${aws_elasticsearch_domain.core_search.endpoint}"
    }
  }
}

resource "aws_iam_role" "lambda_exec_role" {
  name = "lambda_exec_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = "sts:AssumeRole",
        Principal = {
          Service = "lambda.amazonaws.com"
        },
        Effect = "Allow",
        Sid    = ""
      }
    ]
  })
}

resource "aws_iam_policy" "s3_access_policy" {
  name        = "S3AccessPolicyForLambda"
  description = "Allows indexing to access scrape data"

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "s3:ListBucket",
          "s3:GetObject",
        ],
        Resource = [
          "arn:aws:s3:::engcyclopedia-scrape-data",
          "arn:aws:s3:::engcyclopedia-scrape-data/*"
        ]
      }
    ]
  })
}

resource "aws_elasticsearch_domain" "core_search" {
  domain_name           = "core-search"
  elasticsearch_version = "OpenSearch_2.7"

  cluster_config {
    instance_type = "t2.small.elasticsearch"
  }

  ebs_options {
    ebs_enabled = true
    volume_size = 10
  }
}

resource "aws_iam_policy" "opensearch_access_policy" {
  name        = "OpenSearchAccessPolicyForLambda"
  description = "Allows indexing to index scrape data to OpenSearch"

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "es:ESHttpGet",
          "es:ESHttpPut",
          "es:ESHttpPost",
        ],
        Resource = [
          "arn:aws:es:us-east-1:${data.aws_caller_identity.current.account_id}:domain/${aws_elasticsearch_domain.core_search.domain_name}/*"
        ]
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_exec_role_policy" {
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
  role       = aws_iam_role.lambda_exec_role.name
}

resource "aws_iam_role_policy_attachment" "lambda_s3_attach" {
  role       = aws_iam_role.lambda_exec_role.name
  policy_arn = aws_iam_policy.s3_access_policy.arn
}

resource "aws_iam_role_policy_attachment" "lambda_es_attach" {
  role       = aws_iam_role.lambda_exec_role.name
  policy_arn = aws_iam_policy.opensearch_access_policy.arn
}
