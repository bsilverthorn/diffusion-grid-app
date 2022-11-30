locals {
  frontend_dist_path = replace(var.app_frontend_path, "MODULE_PATH", path.module)
}

resource "aws_s3_bucket" "frontend" {
  bucket = "${replace(var.name_stub, "_", "-")}-frontend"
}

resource "aws_s3_object" "frontend" {
  for_each      = fileset(local.frontend_dist_path, "**/*")
  bucket        = aws_s3_bucket.frontend.id
  key           = each.key
  source        = "${local.frontend_dist_path}/${each.key}"
  source_hash   = filemd5("${local.frontend_dist_path}/${each.key}")
  content_type  = var.file_extensions[regex("(.[a-zA-Z0-9]+)$", each.key)[0]]
  cache_control = each.key == "index.html" ? "no-cache" : "max-age=31536000"
}

resource "aws_s3_bucket_policy" "frontend_cloudfront_access" {
  bucket = aws_s3_bucket.frontend.id
  policy = <<-EOF
    {
        "Version": "2012-10-17",
        "Statement": {
            "Sid": "AllowCloudFrontServicePrincipalReadOnly",
            "Effect": "Allow",
            "Principal": {
                "Service": "cloudfront.amazonaws.com"
            },
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::${aws_s3_bucket.frontend.id}/*",
            "Condition": {
                "StringEquals": {
                    "AWS:SourceArn": "${aws_cloudfront_distribution.grid.arn}"
                }
            }
        }
    }
  EOF
}
