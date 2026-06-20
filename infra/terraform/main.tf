# Phase 0 skeleton. Resources are added as later phases need them; the structure
# and the modules below are placeholders that document intended infrastructure.
#
# Planned modules (added in Phase 2+):
#   - vpc                : network with a NAT gateway + Elastic IP (static egress
#                          IP that brokers/SEBI require to be whitelisted)
#   - eks / ecs          : container orchestration
#   - rds (aurora pg)    : relational + TimescaleDB
#   - elasticache redis  : hot cache
#   - msk                : Kafka event bus
#   - s3                 : historical data (Parquet) + artifacts
#   - secretsmanager     : broker API keys / tokens
#   - ecr                : container registry
#
# Example of the static-egress-IP requirement (illustrative, commented out):
#
# resource "aws_eip" "broker_egress" {
#   domain = "vpc"
#   tags   = { Name = "broker-gateway-static-egress" }
# }

output "placeholder" {
  value       = "Terraform skeleton — modules added from Phase 2."
  description = "Confirms the infra layout is wired but not yet provisioning."
}
