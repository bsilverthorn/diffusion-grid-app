resource "aws_route53_zone" "main" {
  name = var.frontend_domain
}

resource "aws_route53_record" "main_root" {
  zone_id = aws_route53_zone.main.zone_id
  name    = aws_route53_zone.main.name
  type    = "A"

  alias {
    name                   = aws_cloudfront_distribution.grid.domain_name
    zone_id                = aws_cloudfront_distribution.grid.hosted_zone_id
    evaluate_target_health = false
  }
}

resource "aws_acm_certificate" "main" {
  domain_name       = aws_route53_zone.main.name
  validation_method = "DNS"
}

resource "aws_route53_record" "main_validation" {
  for_each = {
    for dvo in aws_acm_certificate.main.domain_validation_options : dvo.domain_name => {
      name    = dvo.resource_record_name
      record  = dvo.resource_record_value
      type    = dvo.resource_record_type
      zone_id = aws_route53_zone.main.zone_id
    }
  }

  allow_overwrite = true
  name            = each.value.name
  records         = [each.value.record]
  ttl             = 60
  type            = each.value.type
  zone_id         = each.value.zone_id
}

resource "aws_acm_certificate_validation" "main" {
  certificate_arn         = aws_acm_certificate.main.arn
  validation_record_fqdns = [for record in aws_route53_record.main_validation : record.fqdn]
}