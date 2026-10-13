# OptiLab concepts

## Design intent vs lab runtime

A **design** YAML describes what you intend: sites, fiber spans, wavelengths, and checks. OptiLab **validates** that intent and optionally **renders** a Containerlab topology. Validation never starts containers; deploy is a separate step (`make lab-up`).

Keep loss budgets and wavelength policy in the design file so CI (pytest / Robot) can catch mistakes before image pulls or `containerlab deploy`.

## Span loss model

For each link:

```text
span_loss_db = length_km × fiber_loss_db_km + connectors_db + splices_db
```

Defaults: `fiber_loss_db_km = 0.22`, connectors and splices `0`. This is a first-order engineering estimate, not a full OTDR or amplifier model. Use `span_loss_max` checks to encode budgets (for example, 25 dB for an unamplified metro span in the demo).

## Wavelength uniqueness

`unique_wavelengths` treats `wavelength_nm` as a channel key with exact float equality. Two services on the same value produce `DUP_WAVELENGTH`. There is no ITU grid rounding or tolerance band in the current implementation.

## Path existence

`path_exists` walks `services[].path` in order. Each hop must be a known site ID, and each consecutive pair must have a link in either direction (`a→z` or `z→a`). Multi-hop paths need an explicit link for every hop pair; OptiLab does not invent transit through intermediate sites unless those hops appear in the path and links exist.

## Findings severity

| Severity | Effect on exit code |
|----------|---------------------|
| `INFO` | Does not fail |
| `WARN` | Reserved in the model; current checks emit ERROR or INFO |
| `ERROR` | `validate` exits `1` |

Every link always gets an INFO `SPAN_LOSS` finding so reports show estimated loss even when all checks pass.

## Render defaults

Rendered topologies use management network `clab` on `172.30.30.0/24` (IPv6 `3fff:172:30:30::/64`) to reduce clashes with common Docker `172.20.0.0/16` ranges. Site `id` becomes the node name; `clab_kind` and `image` pass through unchanged.
