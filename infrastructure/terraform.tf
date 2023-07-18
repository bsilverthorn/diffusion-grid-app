terraform {
  required_version = "= 1.3.7"

  cloud {
  }

  required_providers {
    sentry = {
      source = "jianyuan/sentry"
    }
  }
}

provider "aws" {
}

provider "sentry" {
}
