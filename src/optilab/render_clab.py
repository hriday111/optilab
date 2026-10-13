from __future__ import annotations

from pathlib import Path

import yaml

from .model import Design

# Match lab/two-node.clab.yml — avoid Docker subnet clash with common 172.20.0.0/16 nets.
DEFAULT_MGMT = {
    "network": "clab",
    "ipv4-subnet": "172.30.30.0/24",
    "ipv6-subnet": "3fff:172:30:30::/64",
}


def render_clab(design: Design) -> dict:
    nodes = {}
    for s in design.sites:
        nodes[s.id] = {"kind": s.clab_kind, "image": s.image}
    links = []
    for ln in design.links:
        links.append(
            {"endpoints": [f"{ln.a}:{ln.a_endpoint}", f"{ln.z}:{ln.z_endpoint}"]}
        )
    return {
        "name": design.network.name,
        "mgmt": DEFAULT_MGMT,
        "topology": {"nodes": nodes, "links": links},
    }


def write_clab(design: Design, out: str | Path) -> Path:
    out = Path(out)
    out.write_text(yaml.safe_dump(render_clab(design), sort_keys=False))
    return out
