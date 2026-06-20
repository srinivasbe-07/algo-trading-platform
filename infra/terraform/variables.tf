variable "aws_region" {
  description = "AWS region (ap-south-1 = Mumbai, closest to NSE/BSE)."
  type        = string
  default     = "ap-south-1"
}

variable "environment" {
  description = "Deployment environment."
  type        = string
  default     = "staging"
}
