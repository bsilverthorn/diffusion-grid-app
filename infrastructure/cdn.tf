data "aws_region" "current" {
}

locals {
  cloudfront_index_origin_id = "${replace(var.name_stub, "_", "-")}-index"
  cloudfront_api_origin_id   = "${replace(var.name_stub, "_", "-")}-api"
}

resource "aws_cloudfront_origin_access_control" "grid" {
  name                              = var.name_stub
  origin_access_control_origin_type = "s3"
  signing_behavior                  = "always"
  signing_protocol                  = "sigv4"
}

resource "aws_cloudfront_distribution" "grid" {
  origin {
    origin_id                = local.cloudfront_index_origin_id
    domain_name              = aws_s3_bucket.frontend.bucket_regional_domain_name
    origin_access_control_id = aws_cloudfront_origin_access_control.grid.id
  }

  origin {
    origin_id = local.cloudfront_api_origin_id
    domain_name = regex(
      "^https://(?P<domain>[a-zA-Z0-9.-]+)/?$",
    aws_lambda_function_url.grid_request.function_url).domain

    custom_origin_config {
      http_port              = 80
      https_port             = 443
      origin_protocol_policy = "https-only"
      origin_ssl_protocols   = ["TLSv1.2"]
    }

    custom_header {
      name  = "Authorization"
      value = local.lambda_auth_header
    }
  }

  enabled             = true
  default_root_object = "index.html"
  aliases             = [var.frontend_domain]

  default_cache_behavior {
    allowed_methods        = ["GET", "HEAD", "OPTIONS"]
    cached_methods         = ["GET", "HEAD"]
    target_origin_id       = local.cloudfront_index_origin_id
    viewer_protocol_policy = "redirect-to-https"

    forwarded_values {
      query_string = false

      cookies {
        forward = "none"
      }
    }

    min_ttl     = 0
    default_ttl = 3600
    max_ttl     = 86400
  }

  ordered_cache_behavior {
    path_pattern           = "/api/*"
    allowed_methods        = ["DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT"]
    cached_methods         = ["GET", "HEAD", "OPTIONS"]
    target_origin_id       = local.cloudfront_api_origin_id
    viewer_protocol_policy = "redirect-to-https"

    forwarded_values {
      query_string = true

      cookies {
        forward = "none"
      }
    }

    min_ttl     = 0
    default_ttl = 3600
    max_ttl     = 86400
  }

  viewer_certificate {
    acm_certificate_arn = aws_acm_certificate.main.arn
    ssl_support_method  = "sni-only"
  }

  price_class = "PriceClass_All"

  restrictions {
    geo_restriction {
      locations        = []
      restriction_type = "none"
    }
  }
}
