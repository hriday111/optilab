from __future__ import annotations

from dataclasses import dataclass

from .model import Design


@dataclass
class Finding:
    severity: str  # ERROR | WARN | INFO
    code: str
    message: str


def validate_design(design: Design) -> list[Finding]:
    findings: list[Finding] = []
    ids = design.site_ids()

    for ln in design.links:
        if ln.a not in ids or ln.z not in ids:
            findings.append(
                Finding(
                    "ERROR",
                    "LINK_UNKNOWN_SITE",
                    f"{ln.id} references unknown site",
                )
            )
        loss = ln.span_loss_db()
        findings.append(
            Finding(
                "INFO",
                "SPAN_LOSS",
                f"{ln.id} estimated span loss {loss:.2f} dB",
            )
        )

    for chk in design.checks:
        if chk.type == "span_loss_max" and chk.link and chk.max_db is not None:
            link = next((l for l in design.links if l.id == chk.link), None)
            if not link:
                findings.append(
                    Finding("ERROR", "CHECK_BAD_LINK", f"missing {chk.link}")
                )
            elif link.span_loss_db() > chk.max_db:
                findings.append(
                    Finding(
                        "ERROR",
                        "SPAN_LOSS_EXCEEDED",
                        f"{chk.link} loss {link.span_loss_db():.2f} dB > {chk.max_db} dB",
                    )
                )

        if chk.type == "unique_wavelengths":
            seen: dict[float, str] = {}
            for svc in design.services:
                if svc.wavelength_nm in seen:
                    findings.append(
                        Finding(
                            "ERROR",
                            "DUP_WAVELENGTH",
                            f"{svc.id} and {seen[svc.wavelength_nm]} share "
                            f"{svc.wavelength_nm} nm",
                        )
                    )
                else:
                    seen[svc.wavelength_nm] = svc.id

        if chk.type == "path_exists" and chk.service:
            svc = next((s for s in design.services if s.id == chk.service), None)
            if not svc:
                findings.append(Finding("ERROR", "SVC_MISSING", chk.service))
            else:
                for hop in svc.path:
                    if hop not in ids:
                        findings.append(
                            Finding(
                                "ERROR",
                                "PATH_BAD_HOP",
                                f"{svc.id} hop {hop} not in sites",
                            )
                        )
                site_links = {(l.a, l.z) for l in design.links} | {
                    (l.z, l.a) for l in design.links
                }
                for i in range(len(svc.path) - 1):
                    if (svc.path[i], svc.path[i + 1]) not in site_links:
                        findings.append(
                            Finding(
                                "ERROR",
                                "PATH_NOT_LINKED",
                                f"{svc.id}: no link {svc.path[i]}-{svc.path[i + 1]}",
                            )
                        )

    return findings


def has_errors(findings: list[Finding]) -> bool:
    return any(f.severity == "ERROR" for f in findings)
