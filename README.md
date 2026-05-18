# HARMONSMILE: Harmonize SMILES Strings for Cheminformatics and Machine Learning

[![License: LGPL v3](https://img.shields.io/badge/License-LGPL_v3-blue.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-v0.1.0-blue.svg)](https://pypi.org/project/harmonsmile/)
[![PyPI](https://img.shields.io/pypi/v/harmonsmile.svg)](https://pypi.org/project/harmonsmile/)
[![Python](https://img.shields.io/pypi/pyversions/harmonsmile.svg)](https://pypi.org/project/harmonsmile/)

---

HARMONSMILE solves a common problem in cheminformatics: SMILES strings for the same
molecule look different depending on the source (PubChem, COCONUT, ChEMBL, in-house
databases). This inconsistency breaks comparisons, deduplication, and machine learning
pipelines that expect a uniform molecular representation.

HARMONSMILE converts any SMILES to a single canonical form — **canonical + isomeric +
Kekulized** — following the convention used by RDKit and COCONUT 2.0, making your
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

Harmonize a COCONUT or independent database:

```python
from harmonsmile import CoconutPrep

CoconutPrep(
    input_path="data/database_coconut.csv",
    smiles_col="SMILES",
    output_path="results/coconut_harmonized.csv",
).run()
```

Fetch properties from PubChem and harmonize:

```python
from harmonsmile import PubChemIngest, Config

cfg = Config(
    input_path="data/database_pubchem.csv",
    output_path="results/pubchem_harmonized.csv",
)
PubChemIngest(cfg).run()
```

### Command-Line Interface

```bash
# PubChem database
harmonsmile --pubchem-in data/database1.csv --pubchem-out results/database1_harmonized.csv

# COCONUT / independent database
harmonsmile --coconut-in data/database2.csv --coconut-smiles SMILES \
            --coconut-out results/database2_harmonized.csv

# Both pipelines in one run
harmonsmile \
  --pubchem-in  data/database1.csv --pubchem-out  results/database1_harmonized.csv \
  --coconut-in  data/database2.csv --coconut-smiles SMILES \
  --coconut-out results/database2_harmonized.csv
```

Also available as a Python module:

```bash
python -m harmonsmile --pubchem-in data/database1.csv --pubchem-out results/out.csv
```

---

## Input Format

| Pipeline | Required columns |
|---|---|
| PubChem | `id`, `PubChem CID` |
| COCONUT / independent | `id`, `<smiles_col>` (any column name) |

Supported file formats: CSV, TSV, XLSX, XLS.

---

## Roadmap

- **v0.2.0** — `ChEMBLIngest` pipeline with the same RDKit normalization → unified `SMILES_RDKit` output.
- **v0.3.0** — ML-ready features: ECFP fingerprints (with/without chirality), InChI/InChIKey
  for deduplication and robust cross-database matching.

---

## Development

### Project Structure

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
├── tests/                 # Unit test suite (pytest)
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
Contreras-Torres, F. F. (2025). HARMONSMILE: Harmonize SMILES Strings for
Cheminformatics and Machine Learning (v0.1.0). Tecnologico de Monterrey.
https://github.com/NanoBiostructuresRG/harmonsmile
```

---

## Author

Developed by **Flavio F. Contreras-Torres** (Tecnológico de Monterrey)
Monterrey, Mexico – September 2025

---

## License

This project is licensed under the terms of the
[GNU Lesser General Public License v3.0 or later](LICENSE).
SPDX identifier: `LGPL-3.0-or-later`.
