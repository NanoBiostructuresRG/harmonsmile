# HARMONSMILE Public API

This document defines the public API of HARMONSMILE for each release.
Only symbols listed here are considered stable and subject to semantic versioning guarantees.
Private symbols (prefixed with `_`) and deprecated aliases may change or be removed without notice.

---

## v0.1.1 — Current

### Classes

#### `RDKitStandardizer`
```python
from harmonsmile import RDKitStandardizer
```
Standardizes SMILES strings using RDKit to canonical + isomeric + Kekulized form.

| Method | Description |
|---|---|
| `to_iso_kek(smiles: str) -> str \| None` | Canonical + isomeric + Kekulized SMILES |
| `to_conn_kek(smiles: str) -> str \| None` | Canonical + connectivity-only + Kekulized SMILES |

---

#### `Config`
```python
from harmonsmile import Config
```
Immutable configuration dataclass for `PubChemIngest`.

| Parameter | Type | Default |
|---|---|---|
| `input_path` | `str` | required |
| `output_path` | `str` | required |
| `error_log` | `str` | `"logs/errors.txt"` |
| `cid_col` | `str` | `"PubChem CID"` |
| `props` | `tuple[str, ...]` | all PubChem properties |

---

#### `PubChemIngest`
```python
from harmonsmile import PubChemIngest, Config
```
Fetches compound properties from PubChem REST API and appends `SMILES_RDKit`.

| Method | Description |
|---|---|
| `run() -> pd.DataFrame` | Execute the pipeline |

**Input CSV required columns:** `PubChem CID`

**Output columns:** `id`, `PubChem CID`, `SMILES`, `SMILES_RDKit`, `ConnectivitySMILES`,
`MolecularFormula`, `MW`, `InChI`, `InChIKey`, `XLogP`, `TPSA`, `Charge`,
`HBondDonorCount`, `HBondAcceptorCount`, `RotatableBondCount`, `HeavyAtomCount`

---

#### `ChEMBLIngest`
```python
from harmonsmile import ChEMBLIngest
```
Fetches compound properties from ChEMBL REST API and appends `SMILES_RDKit`.

| Method | Description |
|---|---|
| `run() -> pd.DataFrame` | Execute the pipeline |

**Input CSV required columns:** `ChEMBL ID`

**Output columns:** `id`, `ChEMBL ID`, `name`, `SMILES`, `SMILES_RDKit`, `InChI`,
`InChIKey`, `MW`, `MolecularFormula`, `ALogP`, `TPSA`, `HBA`, `HBD`,
`RotatableBonds`, `HeavyAtoms`, `QED`, `Ro5Violations`

---

#### `SMILESPrep`
```python
from harmonsmile import SMILESPrep
```
Harmonizes SMILES from any tabular file (CSV, TSV, XLSX, XLS).

| Method | Description |
|---|---|
| `run() -> pd.DataFrame` | Execute the pipeline |

**Input:** any file with a SMILES column (any name)

**Output:** original columns + `SMILES_RDKit`

---

### Functions

#### `load_table`
```python
from harmonsmile import load_table
```
```python
load_table(path: str | os.PathLike) -> pd.DataFrame
```
Loads CSV, TSV, XLSX, or XLS into a DataFrame.

---

#### `save_table`
```python
from harmonsmile import save_table
```
```python
save_table(df: pd.DataFrame, path: str | os.PathLike) -> None
```
Saves a DataFrame to CSV. Creates parent directories if needed.

---

### Package Metadata

```python
from harmonsmile import __version__, PROJECT_NAME, PROJECT_VERSION, PROJECT_STATUS
```

| Symbol | Value in v0.1.1 |
|---|---|
| `__version__` | `"0.1.1"` |
| `PROJECT_NAME` | `"HARMONSMILE"` |
| `PROJECT_VERSION` | `"0.1.1"` |
| `PROJECT_STATUS` | `"alpha"` |

---

### Command-Line Interface

```bash
harmonsmile --version
harmonsmile --pubchem-in FILE --pubchem-out FILE [--pubchem-cidcol COL]
harmonsmile --chembl-in FILE --chembl-out FILE [--chembl-idcol COL]
harmonsmile --coconut-in FILE --coconut-smiles COL --coconut-out FILE
```

All three pipelines can be combined in a single run.

---

### Deprecated (removed in v0.2.0)

| Symbol | Replaced by |
|---|---|
| `CoconutPrep` | `SMILESPrep` |
| `PubChemClient` | `_PubChemClient` (private) |

---

## Planned — v0.2.0

- `CoconutIngest` — COCONUT 2.0 pipeline (knows schema automatically)
- Single compound CLI lookup: `--chembl-id CHEMBL294199`, `--pubchem-cid 2723949`
- Fix: duplicate `name` column in `ChEMBLIngest` output

## Planned — v0.3.0

- ECFP fingerprint generation (with/without chirality)
- InChI/InChIKey deduplication utilities
