# OptiLab

OptiLab turns a YAML network design into a [Containerlab](https://containerlab.dev/) topology and validates optical/path constraints before you deploy. It is for network engineers and platform teams who want a **design → validate → lab** dry-run loop.

Span loss:

`length_km × fiber_loss_db_km + connectors_db + splices_db`

Deeper background: [docs/concepts.md](docs/concepts.md).

## Prerequisites

- Python 3.12+
- Optional: [Containerlab](https://containerlab.dev/) + Docker (`sudo`) for live labs
- Optional: [kind](https://kind.sigs.k8s.io/) for the Kubernetes dry-run job

## Quickstart (< 5 minutes)

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

PYTHONPATH=src python -m optilab.cli validate designs/demo-ring.yaml
PYTHONPATH=src python -m optilab.cli render designs/demo-ring.yaml -o lab/demo-ring.clab.yml
```

Or: `make validate`, `make render`, `make test`.

`validate` prints findings as JSON, writes `reports/design-report.md` and `reports/findings.json`, and exits **1** if any finding has severity `ERROR`.

## Design YAML

Top-level sections: `network`, `sites`, `links`, `services`, `checks`.

### `network`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | yes | Topology name (Containerlab `name`) |
| `region` | string | no | Free-form region label |
| `description` | string | no | Shown in the Markdown report |

### `sites[]`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | yes | Unique ID; referenced by links and paths |
| `role` | string | yes | e.g. `aggregation`, `tester` |
| `location` | string | no | Human-readable location |
| `clab_kind` | string | yes | Containerlab kind (`nokia_srlinux`, `linux`, …) |
| `image` | string | yes | Container image |

### `links[]`

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `id` | string | yes | — | Link ID (for `span_loss_max`) |
| `a` / `z` | string | yes | — | Site IDs at each end |
| `a_endpoint` / `z_endpoint` | string | yes | — | Interface names |
| `length_km` | float | no | `0` | Span length |
| `fiber_loss_db_km` | float | no | `0.22` | Fiber attenuation |
| `connectors_db` | float | no | `0` | Connector loss |
| `splices_db` | float | no | `0` | Splice loss |

### `services[]`

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `id` | string | yes | — | Service ID |
| `path` | list[string] | yes | — | Ordered site hops |
| `wavelength_nm` | float | yes | — | Wavelength (nm) |
| `bitrate_gbps` | float | no | `100` | Bitrate |

### `checks[]`

| `type` | Fields | Behavior |
|--------|--------|----------|
| `span_loss_max` | `link`, `max_db` | ERROR if span loss > `max_db` |
| `unique_wavelengths` | — | ERROR if two services share `wavelength_nm` |
| `path_exists` | `service` | ERROR if hops unknown or adjacent hops unlinked |

Example (shape of `designs/demo-ring.yaml`):

```yaml
network:
  name: demo-rde-ring
  description: "Regional delivery dry-run lab"

sites:
  - id: byd-01
    role: aggregation
    clab_kind: nokia_srlinux
    image: ghcr.io/nokia/srlinux
  - id: tor-01
    role: aggregation
    clab_kind: nokia_srlinux
    image: ghcr.io/nokia/srlinux

links:
  - id: L1
    a: byd-01
    z: tor-01
    a_endpoint: e1-1
    z_endpoint: e1-1
    length_km: 85
    fiber_loss_db_km: 0.22
    connectors_db: 1.0

services:
  - id: SVC-DEMO-1
    path: [byd-01, tor-01]
    wavelength_nm: 1547.72
    bitrate_gbps: 100

checks:
  - type: span_loss_max
    link: L1
    max_db: 25
  - type: unique_wavelengths
  - type: path_exists
    service: SVC-DEMO-1
```

L1 estimated loss: `85 × 0.22 + 1.0 = 19.70 dB` (under the 25 dB budget). Verified against `src/optilab/model.py`.

## CLI

```text
python -m optilab.cli validate <design.yaml> [--report PATH]
python -m optilab.cli render   <design.yaml> [-o|--out PATH]
```

| Command | Argument | Default | Exit |
|---------|----------|---------|------|
| `validate` | `design` | — | `0` ok; `1` ERROR findings; `2` bad usage |
| `validate` | `--report` | `reports/design-report.md` | — |
| `render` | `design` | — | `0` on success |
| `render` | `-o` / `--out` | `lab/demo-ring.clab.yml` | — |

`render` maps sites → nodes (`kind` + `image`) and links → `endpoints`. Mgmt network defaults to `172.30.30.0/24`.

## Finding codes

| Code | Severity | Meaning | Fix |
|------|----------|---------|-----|
| `SPAN_LOSS` | INFO | Estimated span loss | Informational |
| `LINK_UNKNOWN_SITE` | ERROR | Link `a`/`z` missing from sites | Fix site IDs |
| `CHECK_BAD_LINK` | ERROR | `span_loss_max` link missing | Use a real `links[].id` |
| `SPAN_LOSS_EXCEEDED` | ERROR | Loss > `max_db` | Adjust span or budget |
| `DUP_WAVELENGTH` | ERROR | Shared wavelength | Unique `wavelength_nm` |
| `SVC_MISSING` | ERROR | Unknown service in check | Fix `checks[].service` |
| `PATH_BAD_HOP` | ERROR | Path hop not in sites | Fix `services[].path` |
| `PATH_NOT_LINKED` | ERROR | No link between hops | Add link or fix path |

`designs/bad-dup-lambda.yaml` fails with `DUP_WAVELENGTH` (`SVC-A` / `SVC-B` both at `1547.72` nm).

## Optional lab / cluster

```bash
make lab-up      # render + sudo containerlab deploy
make lab-down
make cluster-up  # kind cluster --name optilab
make dry-run     # pytest + Robot -> reports/
```

See `Dockerfile` and `k8s/dry-run-job.yaml` for a containerized Robot dry-run (`optilab-runner:local`).

## Common pitfalls

1. **Missing `PYTHONPATH=src`** — imports fail unless you set it (Make already does).
2. **Duplicate wavelengths** — exact float match; use distinct DWDM channels.
3. **Path vs topology** — every consecutive hop pair needs an undirected link.
4. **INFO vs exit code** — `SPAN_LOSS` INFO always appears; only `ERROR` fails the run.
5. **Endpoint names** — must match the kind (`e1-1` for SR Linux, `eth1` for Linux). OptiLab does not validate interface names against the image.

## Layout

```text
designs/       Intent YAML (demo + negative fixtures)
src/optilab/   model, validate, render, report, CLI
lab/           .clab.yml topologies
robot/         Robot Framework dry-run
tests/         pytest
k8s/           kind Job
reports/       Generated (gitignored except .gitkeep)
```

---

*AI was used only to draft this documentation; behavior is defined by `src/optilab/`.*
