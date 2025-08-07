# Software Bill of Materials (SBOM) for `pyawg`

**Project Name:** pyawg  
**Version:** 0.4.0.0  
**Maintainer:** Abhishek Bawkar  
**License:** GNU General Public License v3.0 (GPLv3)  
**Purpose:** Internal-use tool for controlling arbitrary waveform generators (AWGs) in automated firmware and hardware-in-the-loop (HiL) testing.

---

## Components Overview

| Dependency        | Version     | License    | Source Repository                               | Function                                          |
|-------------------|-------------|------------|-------------------------------------------------|---------------------------------------------------|
| python            | >=3.8, <4.0 | PSF        | https://www.python.org                          | Programming language used to develop this library |
| python-vxi11      | ≥0.9        | MIT        | https://github.com/python-ivi/python-vxi11      | LAN-based communication with AWGs                 |
| platform (stdlib) | stdlib      | Python PSF | https://docs.python.org/3/library/platform.html | OS and architecture introspection                 |
| typing (stdlib)   | stdlib      | Python PSF | https://docs.python.org/3/library/typing.html   | Type annotations and hints                        |

---

## Packaging and Distribution

- This library is not distributed as part of any hardware or software product.
- It is not installed or deployed on customer systems or embedded devices.
- It is intended to be used only internally as a tool to support development and testing of embedded hardware, firmware and software products, but **not as a part of or a fully commercial product**.

---

## Security Considerations

- The software does **not implement or rely on encryption** or cryptographic protocols.
- It does **not interface with cloud services**, remote systems, or external APIs.
- All data flow occurs locally via LAN or USB to AWGs using the VXI-11 protocol.
- No persistent storage or telemetry is performed.

---

## CRA Relevance

Based on its purpose, scope, and deployment context, `pyawg` is not considered a "product with digital elements" as defined by the **EU Cyber Resilience Act (CRA)**. As such, the obligations outlined in the CRA are not applicable to this project.

This SBOM is provided for transparency and traceability in alignment with secure software development practices.

---

_Last updated: [07. Aug 2025]_
