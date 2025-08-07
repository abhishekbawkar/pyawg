# Contributor Guidelines

Thank you for your interest in contributing to `pyawg`.

This project is licensed under the GNU General Public License v3.0 (GPLv3). All contributions must comply with this license and the following guidelines:

## 🛠️ Modifying Existing Files

If you modify an existing source file, please preserve the original copyright notice and **add** your own:

```python
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2025 Abhishek Bawkar
# Copyright (C) 2025 Your Name or Organization
```

Do not remove or replace existing lines.

## 🆕 Adding New Files

New files must include:

```python
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2025 Your Name or Organization
```

This ensures clear traceability and licensing consistency across the codebase.

## 📜 License Consistency

All contributions must be compatible with GPLv3. By submitting code, you agree that your work may be distributed under the same terms.

For questions about licensing or contributions, please open an issue or contact the maintainer.


## EU Cyber Resilience Act (CRA) Compliance Alignment

This project is intended solely for internal test automation and is **not** part of any commercial product.  
To maintain alignment with the EU Cyber Resilience Act (CRA) scope:

- Do not add features that involve encryption, secure communication protocols, or cloud-based data transfer.
- Do not integrate functionality that would make this library part of a product delivered to customers.
- Keep all contributions in line with the intended usage described in the README.md.

Any contribution that could affect CRA applicability may be rejected or require a separate discussion before merging.
