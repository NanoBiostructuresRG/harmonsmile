# HARMONSMILE: Harmonize SMILES Strings for Cheminformatics and Machine Learning

[![License: LGPL v3](https://img.shields.io/badge/License-LGPL_v3-blue.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-v0.2.2-blue.svg)](https://pypi.org/project/harmonsmile/)
[![PyPI](https://img.shields.io/pypi/v/harmonsmile.svg)](https://pypi.org/project/harmonsmile/)
[![Python](https://img.shields.io/pypi/pyversions/harmonsmile.svg)](https://pypi.org/project/harmonsmile/)
[![Docs](https://img.shields.io/badge/docs-GitHub%20Pages-teal.svg)](https://nanobiostructuresrg.github.io/harmonsmile/)

---

## Description

**HARMONSMILE** solves a common problem in cheminformatics: SMILES strings for the same
molecule look different depending on the source (PubChem, ChEMBL, COCONUT, in-house
databases). This inconsistency breaks comparisons, deduplication, and machine learning
pipelines that expect a uniform molecular representation.

---

## Purpose

The primary objective of **HARMONSMILE** is to automate the preparation of molecular datasets for cheminformatics workflows and **phase 1** machine learning applications within the computational drug discovery pipeline. 

The platform enables:

- **Data Harmonization**: Standardizes SMILES strings to a consistent format — **canonical + isomeric +
Kekulized** — ensuring that the same molecule is represented identically across different datasets and sources. It follows the RDKit convention for canonicalization, which is widely adopted in the cheminformatics community.

---

## Installation

```bash
pip install harmonsmile
```

> RDKit is required and installed automatically (`rdkit>=2022.09`).

---

## Quick Start

### Python API

Standardize a single SMILES string:

```python
from harmonsmile import RDKitStandardizer

std = RDKitStandardizer()
print(std.to_iso_kek("c1ccccc1"))    # canonical + isomeric + Kekulized
print(std.to_conn_kek("c1ccccc1"))   # canonical + connectivity-only + Kekulized
```

Fetch properties from PubChem and harmonize:

```python
from harmonsmile import PubChemIngest, PubChemConfig

cfg = PubChemConfig(
    input_path="examples/example_pubchem.csv",   # requires: id, PubChem CID
    output_path="results/example_pubchem_harmonized.csv",
)
PubChemIngest(cfg).run()
```

Fetch properties from ChEMBL and harmonize:

```python
from harmonsmile import ChEMBLIngest, ChEMBLConfig

cfg = ChEMBLConfig(
    input_path="examples/example_chembl.csv",    # requires: id, ChEMBL ID
    output_path="results/example_chembl_harmonized.csv",
)
ChEMBLIngest(cfg).run()
```

Harmonize any file with a SMILES column (COCONUT, in-house, etc.):

```python
from harmonsmile import SMILESPrep, SMILESConfig

cfg = SMILESConfig(
    input_path="examples/example_smiles.csv",
    smiles_col="SMILES",                      # any column name
    output_path="results/example_smiles_harmonized.csv",
)
SMILESPrep(cfg).run()
```

### Command-Line Interface

```bash
# PubChem pipeline
harmonsmile --pubchem-in examples/database1.csv --pubchem-out results/database1_harmonized.csv

# SMILES pipeline (COCONUT, independent, etc.)
harmonsmile --smiles-in examples/database2.csv --smiles-col canonical_smiles \
            --smiles-out results/database2_harmonized.csv

# Both pipelines in one run
harmonsmile \
  --pubchem-in examples/database1.csv --pubchem-out results/database1_harmonized.csv \
  --smiles-in  examples/database2.csv --smiles-col  canonical_smiles \
  --smiles-out results/database2_harmonized.csv

# Single Entry — fetch one compound by ID
harmonsmile --pubchem-cid 2723949
harmonsmile --chembl-id CHEMBL294199

# Check version
harmonsmile --version
```

Also available as a Python module:

```bash
python -m harmonsmile --pubchem-in examples/database1.csv --pubchem-out results/out.csv
```

---

## Pipelines

| Pipeline | Config | Source | Input | API |
|---|---|---|---|---|
| `PubChemIngest` | `PubChemConfig` | PubChem | CSV with `PubChem CID` column | REST (public) |
| `ChEMBLIngest` | `ChEMBLConfig` | ChEMBL | CSV with `ChEMBL ID` column | REST (public) |
| `SMILESPrep` | `SMILESConfig` | Any | CSV/Excel with any SMILES column | — (local file) |

All pipelines append a `SMILES_RDKit` column with the harmonized SMILES.

---

## Input Format

| Pipeline | Required columns |
|---|---|
| `PubChemIngest` | `id` (optional), `PubChem CID` |
| `ChEMBLIngest` | `id` (optional), `ChEMBL ID` |
| `SMILESPrep` | `id` (optional), `<smiles_col>` (any name) |

Supported file formats: CSV, TSV, XLSX, XLS.

---

## Roadmap

- **v0.3.0** — ML-ready features: ECFP fingerprints (with/without chirality),
  InChI/InChIKey for deduplication and robust cross-database matching.

---

## Development

### Project Structure

```text
HARMONSMILE/
├── harmonsmile/
│   ├── __init__.py        # Public API
│   ├── __main__.py        # python -m harmonsmile entry point
│   ├── _cli.py            # CLI implementation
│   ├── chembl.py          # ChEMBL REST client
│   ├── config.py          # PubChemConfig, ChEMBLConfig, SMILESConfig dataclasses
│   ├── io.py              # Table I/O utilities
│   ├── pipelines.py       # PubChemIngest, ChEMBLIngest, SMILESPrep
│   ├── pubchem.py         # PubChem REST client
│   ├── standardize.py     # RDKitStandardizer
│   └── version.py         # Package version metadata
├── tests/                 # Unit test suite (pytest) — 146 tests
├── examples/              # Example scripts and datasets
├── results/               # Output data (not installed)
├── logs/                  # Error logs (not installed)
├── pyproject.toml
├── environment.yml
├── mkdocs.yml
├── requirements-dev.txt
├── CHANGELOG.md
├── CITATION.cff
├── COPYING
├── COPYING.LESSER
├── LICENSE
└── README.md
```

### Running Tests

```bash
python -m pytest tests -p no:cacheprovider --basetemp .pytest_tmp
```

### Contributing

Contributions are welcome. Please open an issue before submitting a pull request.
Follow the existing code style: NumPy-style docstrings, type hints, and SPDX license
headers in all source files.

---

## Citation

If you use HARMONSMILE in your research, please cite it using the metadata in
[CITATION.cff](CITATION.cff) or the format below:

```
Contreras-Torres, F. F. (2026). HARMONSMILE: Harmonize SMILES Strings for
Cheminformatics and Machine Learning (v0.2.2). Tecnologico de Monterrey.
https://github.com/NanoBiostructuresRG/harmonsmile
```

---

## Author

Developed by **Flavio F. Contreras-Torres** (Tecnológico de Monterrey)
Monterrey, Mexico – May 2026

---

## License

This project is licensed under the terms of the
[GNU Lesser General Public License v3.0 or later](LICENSE).
SPDX identifier: `LGPL-3.0-or-later`.
