"""Template microservice.

Every other service is cloned from this one: a typed FastAPI app, a /health
endpoint for liveness/readiness probes, config from the environment, and tests.
"""

from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel

from app.config import settings

app = FastAPI(title=settings.service_name, version=settings.version)


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    environment: str


@app.get("/health", response_model=HealthResponse, tags=["ops"])
def health() -> HealthResponse:
    """Liveness/readiness probe used by Kubernetes and the load balancer."""
    return HealthResponse(
        status="ok",
        service=settings.service_name,
        version=settings.version,
        environment=settings.environment,
    )
