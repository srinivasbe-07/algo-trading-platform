# AWS provider + remote state. Fill in the backend bucket before first `init`.
terraform {
  required_version = ">= 1.7"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  # backend "s3" {
  #   bucket         = "algo-trading-tfstate"
  #   key            = "global/terraform.tfstate"
  #   region         = "ap-south-1"
  #   dynamodb_table = "algo-trading-tflock"
  #   encrypt        = true
  # }
}

provider "aws" {
  region = var.aws_region
  default_tags {
    tags = {
      Project     = "algo-trading-platform"
      Environment = var.environment
      ManagedBy   = "terraform"
    }
  }
}
