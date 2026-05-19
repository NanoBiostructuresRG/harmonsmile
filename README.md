# HARMONSMILE: Harmonize SMILES Strings for Cheminformatics and Machine Learning

[![License: LGPL v3](https://img.shields.io/badge/License-LGPL_v3-blue.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-v0.1.2-blue.svg)](https://pypi.org/project/harmonsmile/)
[![PyPI](https://img.shields.io/pypi/v/harmonsmile.svg)](https://pypi.org/project/harmonsmile/)
[![Python](https://img.shields.io/pypi/pyversions/harmonsmile.svg)](https://pypi.org/project/harmonsmile/)

---

HARMONSMILE solves a common problem in cheminformatics: SMILES strings for the same
molecule look different depending on the source (PubChem, ChEMBL, COCONUT, in-house
databases). This inconsistency breaks comparisons, deduplication, and machine learning
pipelines that expect a uniform molecular representation.

HARMONSMILE converts any SMILES to a single canonical form — **canonical + isomeric +
Kekulized** — following the convention used by RDKit, making your
datasets consistent and reproducible across sources.

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
from harmonsmile import PubChemIngest, Config

cfg = Config(
    input_path="examples/example_pubchem.csv",   # requires: id, PubChem CID
    output_path="results/example_pubchem_harmonized.csv",
)
PubChemIngest(cfg).run()
```

Fetch properties from ChEMBL and harmonize:

```python
from harmonsmile import ChEMBLIngest

ChEMBLIngest(
    input_path="examples/example_chembl.csv",    # requires: id, ChEMBL ID
    output_path="results/example_chembl_harmonized.csv",
).run()
```

Harmonize any file with a SMILES column (COCONUT, in-house, etc.):

```python
from harmonsmile import SMILESPrep

SMILESPrep(
    input_path="examples/example_smiles.txt",
    smiles_col="SMILES",                      # any column name
    output_path="results/example_smiles_harmonized.csv",
).run()
```

### Command-Line Interface

```bash
# PubChem pipeline
harmonsmile --pubchem-in data/database1.csv --pubchem-out results/database1_harmonized.csv

# SMILES pipeline (COCONUT, independent, etc.)
harmonsmile --smiles-in data/database2.csv --smiles-col canonical_smiles \
            --smiles-out results/database2_harmonized.csv

# Both pipelines in one run
harmonsmile \
  --pubchem-in data/database1.csv --pubchem-out results/database1_harmonized.csv \
  --smiles-in  data/database2.csv --smiles-col  canonical_smiles \
  --smiles-out results/database2_harmonized.csv

# Single Entry — fetch one compound by ID
harmonsmile --pubchem-cid 2723949
harmonsmile --chembl-id CHEMBL294199

# Check version
harmonsmile --version
```

Also available as a Python module:

```bash
python -m harmonsmile --pubchem-in data/database1.csv --pubchem-out results/out.csv
```

---

## Pipelines

| Pipeline | Source | Input | API |
|---|---|---|---|
| `PubChemIngest` | PubChem | CSV with `PubChem CID` column | REST (public) |
| `ChEMBLIngest` | ChEMBL | CSV with `ChEMBL ID` column | REST (public) |
| `SMILESPrep` | Any | CSV/Excel with any SMILES column | — (local file) |

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

- **v0.2.0** — `CoconutIngest`: knows COCONUT 2.0 schema automatically
  (`canonical_smiles`, `identifier`, molecular properties).
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
│   ├── config.py          # Config dataclass
│   ├── io.py              # Table I/O utilities
│   ├── pipelines.py       # PubChemIngest, ChEMBLIngest, SMILESPrep
│   ├── pubchem.py         # PubChem REST client
│   ├── standardize.py     # RDKitStandardizer
│   └── version.py         # Package version metadata
├── tests/                 # Unit test suite (pytest) — 109 tests
├── examples/              # Example scripts and datasets
├── results/               # Output data (not installed)
├── logs/                  # Error logs (not installed)
├── pyproject.toml
├── environment.yml
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
pip install pytest
pytest -v
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
Cheminformatics and Machine Learning (v0.1.2). Tecnologico de Monterrey.
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
