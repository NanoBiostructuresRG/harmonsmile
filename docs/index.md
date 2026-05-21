# HARMONSMILE

**Harmonize SMILES Strings for Cheminformatics and Machine Learning**

---

## Description

**HARMONSMILE** solves a common problem in cheminformatics: SMILES strings for the same
molecule look different depending on the source (PubChem, ChEMBL, COCONUT, in-house
databases). This inconsistency breaks comparisons, deduplication, and machine learning
pipelines that expect a uniform molecular representation.

---

## Purpose

The primary objective of **HARMONSMILE** is to automate the preparation of molecular
datasets for cheminformatics workflows and **phase 1** machine learning applications
within the computational drug discovery pipeline.

The platform enables:

- **Data Harmonization**: Standardizes SMILES strings to a consistent format —
  **canonical + isomeric + Kekulized** — ensuring that the same molecule is represented
  identically across different datasets and sources. It follows the RDKit convention
  for canonicalization, which is widely adopted in the cheminformatics community.

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

Harmonize any file with a SMILES column:

```python
from harmonsmile import SMILESPrep, SMILESConfig

cfg = SMILESConfig(
    input_path="examples/example_smiles.csv",
    smiles_col="SMILES",
    output_path="results/example_smiles_harmonized.csv",
)
SMILESPrep(cfg).run()
```

### Command-Line Interface

```bash
# PubChem batch
harmonsmile --pubchem-in examples/db.csv --pubchem-out results/out.csv

# ChEMBL batch
harmonsmile --chembl-in examples/db.csv --chembl-out results/out.csv

# SMILES batch
harmonsmile --smiles-in examples/db.csv --smiles-col SMILES --smiles-out results/out.csv

# Single Entry
harmonsmile --pubchem-cid 2723949
harmonsmile --chembl-id CHEMBL294199

# As a Python module
python -m harmonsmile --pubchem-in examples/db.csv --pubchem-out results/out.csv
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

## Citation

If you use HARMONSMILE in your research, please cite:

```
Contreras-Torres, F. F. (2026). HARMONSMILE: Harmonize SMILES Strings for
Cheminformatics and Machine Learning (v0.2.2). Tecnologico de Monterrey.
https://github.com/NanoBiostructuresRG/harmonsmile
```

---

## License

This project is licensed under the terms of the
[GNU Lesser General Public License v3.0 or later](https://github.com/NanoBiostructuresRG/harmonsmile/blob/main/LICENSE).  
SPDX identifier: `LGPL-3.0-or-later`.
