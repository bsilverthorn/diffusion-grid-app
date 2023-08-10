#
# IMAGE CACHE
#

locals {
  lambda_function_name = "${var.name_stub}_request"
}

resource "aws_s3_bucket" "cache" {
  bucket = "${replace(var.name_stub, "_", "-")}-cache"

  lifecycle {
    prevent_destroy = true
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "cache" {
  bucket = aws_s3_bucket.cache.id

  rule {
    id     = "expire"
    status = "Enabled"

    expiration {
      days = var.backend_cache_days
    }
  }
}

#
# LAMBDA SOURCE PACKAGE
#

resource "random_string" "lambda_tmp_suffix" {
  length  = 8
  special = false
}

locals {
  backend_path = replace(var.app_backend_path, "MODULE_PATH", path.module)
  lambda_hash = sha1(
    join(
      "",
      [for f in fileset(local.backend_path, "**/*") : filesha1("${local.backend_path}/${f}")],
    )
  )
  lambda_tmp = "${var.system_tmp}/lambda-${random_string.lambda_tmp_suffix.result}"
  lambda_zip = "${var.system_tmp}/lambda.${local.lambda_hash}.zip"
}

resource "null_resource" "lambda_package" {
  provisioner "local-exec" {
    command = <<-EOF
      set -eux
      rm -r '${local.lambda_tmp}' '${local.lambda_zip}' || true
      mkdir -p '${local.lambda_tmp}/{backend,pipenv}'
      cp -r '${local.backend_path}' '${local.lambda_tmp}/backend'
      cd '${local.lambda_tmp}'
      ${var.system_pip} install pipenv -t pipenv
      cd backend
      ../pipenv/bin/pipenv requirements > requirements.txt
      ${var.system_pip} install -r requirements.txt -t .
      ${var.system_zip} --quiet -roX '${local.lambda_zip}' .
      rm -r '${local.lambda_tmp}'
    EOF
  }

  triggers = {
    lambda_hash = local.lambda_hash
  }
}

#
# IAM AND LOGGING
#

resource "aws_cloudwatch_log_group" "lambda" {
  name              = "/aws/lambda/${local.lambda_function_name}"
  retention_in_days = 14
}

resource "aws_iam_role_policy" "lambda_logging" {
  name = "grid_request_log"
  role = aws_iam_role.grid_request_execution.id

  policy = <<-EOF
    {
      "Version": "2012-10-17",
      "Statement": [
        {
          "Action": [
            "logs:CreateLogStream",
            "logs:PutLogEvents"
          ],
          "Resource": "${aws_cloudwatch_log_group.lambda.arn}:*",
          "Effect": "Allow"
        }
      ]
    }
  EOF
}

resource "aws_iam_role_policy" "lambda_cache" {
  name = "grid_request_cache"
  role = aws_iam_role.grid_request_execution.id

  policy = <<-EOF
    {
      "Version": "2012-10-17",
      "Statement": [
        {
          "Action": [
            "s3:PutObject",
            "s3:GetObject",
            "s3:ListBucket"
          ],
          "Resource": [
            "${aws_s3_bucket.cache.arn}",
            "${aws_s3_bucket.cache.arn}/*"
          ],
          "Effect": "Allow"
        }
      ]
    }
  EOF
}

resource "aws_iam_role" "grid_request_execution" {
  name = "${var.name_stub}_request_execution"

  assume_role_policy = <<-EOF
    {
      "Version": "2012-10-17",
      "Statement": [
        {
          "Action": "sts:AssumeRole",
          "Principal": {
            "Service": ["lambda.amazonaws.com", "edgelambda.amazonaws.com"]
          },
          "Effect": "Allow"
        }
      ]
    }
  EOF
}

resource "aws_lambda_permission" "lambda_permission" {
  # permit public invocation so that CloudFront can access it;
  # we'll separately restrict access via auth header

  statement_id           = "AllowPublicInvoke"
  action                 = "lambda:InvokeFunctionUrl"
  function_name          = aws_lambda_function.grid_request.function_name
  principal              = "*"
  function_url_auth_type = aws_lambda_function_url.grid_request.authorization_type
}

#
# SENTRY ERROR REPORTING
#

data "sentry_organization" "main" {
  slug = var.sentry_organization_slug
}

data "sentry_team" "main" {
  organization = data.sentry_organization.main.id
  slug         = var.sentry_team_slug
}

resource "sentry_project" "main" {
  organization = data.sentry_team.main.organization
  teams        = [data.sentry_team.main.id]
  name         = "Diffusion Grid"
  platform     = "python-awslambda"
}

resource "sentry_key" "lambda" {
  organization = data.sentry_team.main.organization
  project      = sentry_project.main.id
  name         = "AWS Lambda"
}

#
# LAMBDA FUNCTION
#

resource "random_password" "signing_key" {
  length = 16
}

resource "random_password" "auth_password" {
  length = 16
}

locals {
  lambda_auth_header = "Basic ${base64encode("cloudfront:${random_password.auth_password.result}")}"
}

resource "aws_lambda_function" "grid_request" {
  filename      = local.lambda_zip
  function_name = local.lambda_function_name
  role          = aws_iam_role.grid_request_execution.arn
  handler       = "dgrid.handler.handle_event"
  runtime       = "python3.10"
  timeout       = 3 * 60

  environment {
    variables = {
      BANANA_API_URL        = var.banana_api_url,
      BANANA_API_KEY        = var.banana_api_key,
      BANANA_MODEL_KEY      = var.banana_model_key,
      DIFFGRID_SIGNING_KEY  = random_password.signing_key.result,
      DIFFGRID_CACHE_BUCKET = aws_s3_bucket.cache.id
      DIFFGRID_AUTH_HEADER  = local.lambda_auth_header
      SENTRY_DSN            = sentry_key.lambda.dsn_public
    }
  }

  depends_on = [
    null_resource.lambda_package
  ]
}

resource "aws_lambda_function_url" "grid_request" {
  function_name      = aws_lambda_function.grid_request.function_name
  authorization_type = "NONE"
}
