from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field


class Site(BaseModel):
    id: str
    role: str
    location: str | None = None
    clab_kind: str
    image: str


class Link(BaseModel):
    id: str
    a: str
    z: str
    a_endpoint: str
    z_endpoint: str
    length_km: float = 0
    fiber_loss_db_km: float = 0.22
    connectors_db: float = 0
    splices_db: float = 0

    def span_loss_db(self) -> float:
        return self.length_km * self.fiber_loss_db_km + self.connectors_db + self.splices_db


class Service(BaseModel):
    id: str
    path: list[str]
    wavelength_nm: float
    bitrate_gbps: float = 100


class Check(BaseModel):
    type: str
    link: str | None = None
    max_db: float | None = None
    service: str | None = None


class NetworkMeta(BaseModel):
    name: str
    region: str | None = None
    description: str | None = None


class Design(BaseModel):
    network: NetworkMeta
    sites: list[Site]
    links: list[Link]
    services: list[Service] = Field(default_factory=list)
    checks: list[Check] = Field(default_factory=list)

    def site_ids(self) -> set[str]:
        return {s.id for s in self.sites}


def load_design(path: str | Path) -> Design:
    data: dict[str, Any] = yaml.safe_load(Path(path).read_text())
    return Design.model_validate(data)
