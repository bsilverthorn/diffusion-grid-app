#
# APPLICATION
#

variable "name_stub" {
  default     = "diffusion_grid"
  description = "prefix for named resources"
}

variable "frontend_domain" {
  default = "diffusion-grid.silverthorn.blog"
}

variable "backend_cache_days" {
  default = null
}

variable "app_backend_path" {
  default = "MODULE_PATH/../backend"
}

variable "app_frontend_path" {
  default = "MODULE_PATH/../frontend/dist"
}

#
# SYSTEM
#

variable "system_tmp" {
  default = "/tmp"
}

variable "system_pip" {
  default = "pip"
}

variable "system_zip" {
  default = "zip"
}

variable "file_extensions" {
  default = {
    ".html" = "text/html; charset=utf-8",
    ".css"  = "text/css; charset=utf-8",
    ".js"   = "application/javascript",
    ".json" = "application/json",
    ".png"  = "image/png",
  }
}

#
# BANANA.DEV
#

variable "banana_api_url" {
  type = string
}

variable "banana_api_key" {
  type      = string
  sensitive = true
}

variable "banana_model_key" {
  type = string
}

#
# SENTRY
#

variable "sentry_organization_slug" {
  type = string
}

variable "sentry_team_slug" {
  type = string
}
