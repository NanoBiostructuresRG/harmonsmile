# HARMONSMILE: Harmonize SMILES Strings for Cheminformatics and Machine Learning

**Version 0.1.0 – September, 2025. Monterrey**

[![License: LGPL v3](https://img.shields.io/badge/License-LGPL_v3-blue.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-v0.1.0-blue.svg)](https://pypi.org/project/harmonsmile/)
[![PyPI](https://img.shields.io/pypi/v/harmonsmile.svg)](https://pypi.org/project/harmonsmile/)
[![Python](https://img.shields.io/pypi/pyversions/harmonsmile.svg)](https://pypi.org/project/harmonsmile/)

---

## Description

**HARMONSMILE** is a toolkit for aligning SMILES strings to a consistent convention:
canonical + isomeric + Kekulized (as used by RDKit and COCONUT 2.0).

---

## Installation

```bash
pip install harmonsmile
```

> **Note:** RDKit is required. It is installed automatically via PyPI (`rdkit>=2022.09`).

---

## Purpose

The primary objective of HARMONSMILE is to automate the preparation of SMILES for
cheminformatics workflows and **phase 1** machine learning applications within the
computational drug discovery pipeline. The platform enables:

- **Standardized SMILES** for comparing data from multiple sources.
- **Reproducibility** in academic and industrial experiments.

---

## Quick Start (Python API)

```python
from harmonsmile import RDKitStandardizer

std = RDKitStandardizer()
print(std.to_iso_kek("c1ccccc1"))        # canonical + isomeric + Kekulized
print(std.to_conn_kek("c1ccccc1"))       # canonical + connectivity-only + Kekulized
```

```python
from harmonsmile import CoconutPrep

CoconutPrep(
    input_path="data/database_coconut.csv",
    smiles_col="SMILES",
    output_path="results/coconut_harmonized.csv",
).run()
```

```python
from harmonsmile import PubChemIngest, Config

cfg = Config(
    input_path="data/database_pubchem.csv",
    output_path="results/pubchem_harmonized.csv",
)
PubChemIngest(cfg).run()
```

---

## Command-Line Interface

```bash
# PubChem database
harmonsmile --pubchem-in data/database1.csv --pubchem-out results/database1_homosmiles.csv

# COCONUT / independent database
harmonsmile --coconut-in data/database2.csv --coconut-smiles SMILES --coconut-out results/database2_homosmiles.csv

# Both in one run
harmonsmile \
  --pubchem-in data/database1.csv --pubchem-out results/database1_homosmiles.csv \
  --coconut-in data/database2.csv --coconut-smiles SMILES --coconut-out results/database2_homosmiles.csv
```

Also available as a module:

```bash
python -m harmonsmile --pubchem-in data/database1.csv --pubchem-out results/out.csv
```

---

## Project Structure

```text
HARMONSMILE/
├── harmonsmile/
│   ├── __init__.py        # Public API
│   ├── __main__.py        # python -m harmonsmile entry point
│   ├── _cli.py            # CLI implementation
│   ├── config.py          # Config dataclass
│   ├── io.py              # Table I/O utilities
│   ├── pipelines.py       # PubChemIngest, CoconutPrep
│   ├── pubchem.py         # PubChem REST client
│   └── standardize.py     # RDKitStandardizer
├── cli/                   # Development scripts (not installed)
├── data/                  # Input data (not installed)
├── results/               # Output data (not installed)
├── logs/                  # Error logs (not installed)
├── pyproject.toml
├── CHANGELOG.md
├── CITATION.cff
├── COPYING
├── COPYING.LESSER
├── LICENSE
└── README.md
```

---

## Input Format

| Pipeline | Required columns |
|---|---|
| PubChem | `id`, `PubChem CID` |
| COCONUT / independent | `id`, `<smiles_col>` (any name) |

---

## Example Console Output

```
[OK] results/database1_homosmiles.csv | SMILES fuente: 66/66 | RDKit: 66/66
```

---

## Future Extensions

- Additional sources (e.g., ChEMBL) with the same RDKit normalization → unified `SMILES_RDKit` output.
- ML-ready features: standardized pipeline to generate ECFP fingerprints (with/without chirality),
  plus InChI/InChIKey for deduplication and robust cross-database matching.

---

## Author

Developed by **Flavio F. Contreras-Torres** (Tecnológico de Monterrey)
Monterrey, Mexico – September 2025

---

## License

This project is licensed under the terms of the [GNU Lesser General Public License v3.0 or later](LICENSE). SPDX identifier: `LGPL-3.0-or-later`.
