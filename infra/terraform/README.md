# Infrastructure (Terraform, AWS)

Skeleton only in Phase 0. Region defaults to `ap-south-1` (Mumbai) to minimise
latency to NSE/BSE.

Key forward-looking decision: the broker-gateway service must egress through a
NAT gateway with a fixed **Elastic IP**, because SEBI/broker rules require order
traffic to originate from a registered **static IP**.

Usage (once modules are added):
```bash
cd infra/terraform
terraform init
terraform plan  -var environment=staging
terraform apply -var environment=staging
```
