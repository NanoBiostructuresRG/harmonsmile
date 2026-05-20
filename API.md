# HARMONSMILE Public API

This document defines the public API of HARMONSMILE for each release.
Only symbols listed here are considered stable and subject to semantic versioning guarantees.
Private symbols (prefixed with `_`) and deprecated aliases may change or be removed without notice.

---

## v0.2.0 — Current

### Classes

#### `PubChemConfig`
```python
from harmonsmile import PubChemConfig
```
Immutable configuration dataclass for `PubChemIngest`.

| Parameter | Type | Default | Validation |
|---|---|---|---|
| `input_path` | `str` | required | Must not be empty or contain `..` |
| `output_path` | `str` | required | Must not be empty or contain `..` |
| `error_log` | `str` | `"logs/errors.txt"` | — |
| `cid_col` | `str` | `"PubChem CID"` | Must not be empty or whitespace-only |
| `props` | `tuple[str, ...]` | all PubChem properties | Must contain at least one valid property |

**Raises:** `ValueError` on any validation failure.

---

#### `ChEMBLConfig`
```python
from harmonsmile import ChEMBLConfig
```
Immutable configuration dataclass for `ChEMBLIngest`.

| Parameter | Type | Default | Validation |
|---|---|---|---|
| `input_path` | `str` | required | Must not be empty or contain `..` |
| `output_path` | `str` | required | Must not be empty or contain `..` |
| `chembl_id_col` | `str` | `"ChEMBL ID"` | Must not be empty or whitespace-only |
| `error_log` | `str` | `"logs/errors.txt"` | — |

**Raises:** `ValueError` on any validation failure.

---

#### `SMILESConfig`
```python
from harmonsmile import SMILESConfig
```
Immutable configuration dataclass for `SMILESPrep`.

| Parameter | Type | Default | Validation |
|---|---|---|---|
| `input_path` | `str` | required | Must not be empty or contain `..` |
| `output_path` | `str` | required | Must not be empty or contain `..` |
| `smiles_col` | `str` | required | Must not be empty or whitespace-only |
| `error_log` | `str` | `"logs/errors.txt"` | — |

**Raises:** `ValueError` on any validation failure.

---

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

#### `PubChemIngest`
```python
from harmonsmile import PubChemIngest, PubChemConfig
```
Fetches compound properties from PubChem REST API and appends `SMILES_RDKit`.

| Method | Description |
|---|---|
| `run() -> pd.DataFrame` | Execute the pipeline |

**`run()` raises:**
- `ValueError` — if the CID column is not found in the input file
- `ValueError` — if the input file has zero rows

**Input CSV required columns:** `PubChem CID`

**Output columns:** `id`, `PubChem CID`, `SMILES`, `SMILES_RDKit`, `ConnectivitySMILES`,
`MolecularFormula`, `MW`, `InChI`, `InChIKey`, `XLogP`, `TPSA`, `Charge`,
`HBondDonorCount`, `HBondAcceptorCount`, `RotatableBondCount`, `HeavyAtomCount`

---

#### `ChEMBLIngest`
```python
from harmonsmile import ChEMBLIngest, ChEMBLConfig
```
Fetches compound properties from ChEMBL REST API and appends `SMILES_RDKit`.

| Method | Description |
|---|---|
| `run() -> pd.DataFrame` | Execute the pipeline |

**`run()` raises:**
- `ValueError` — if the ChEMBL ID column is not found in the input file
- `ValueError` — if the input file has zero rows

**Input CSV required columns:** `ChEMBL ID`

**Output columns:** `id`, `ChEMBL ID`, `name`, `SMILES`, `SMILES_RDKit`, `InChI`,
`InChIKey`, `MW`, `MolecularFormula`, `ALogP`, `TPSA`, `HBA`, `HBD`,
`RotatableBonds`, `HeavyAtoms`, `QED`, `Ro5Violations`

---

#### `SMILESPrep`
```python
from harmonsmile import SMILESPrep, SMILESConfig
```
Harmonizes SMILES from any tabular file (CSV, TSV, XLSX, XLS).

| Method | Description |
|---|---|
| `run() -> pd.DataFrame` | Execute the pipeline |

**`run()` raises:**
- `ValueError` — if the specified SMILES column is not found in the input file
- `ValueError` — if the input file has zero rows

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

**Raises:**
- `FileNotFoundError` — if the file does not exist
- `ValueError` — if the file format is not supported
- `ValueError` — if the loaded DataFrame has zero rows

---

#### `save_table`
```python
from harmonsmile import save_table
```
```python
save_table(df: pd.DataFrame, path: str | os.PathLike) -> None
```
Saves a DataFrame to CSV. Creates parent directories automatically if they do not exist.

---

### Package Metadata

```python
from harmonsmile import __version__, PROJECT_NAME, PROJECT_VERSION, PROJECT_STATUS
```

| Symbol | Value |
|---|---|
| `__version__` | `"0.2.0"` |
| `PROJECT_NAME` | `"HARMONSMILE"` |
| `PROJECT_VERSION` | `"0.2.0"` |
| `PROJECT_STATUS` | `"alpha"` |

---

### Command-Line Interface

```bash
# Information
harmonsmile --version
harmonsmile --help

# PubChem batch
harmonsmile --pubchem-in FILE --pubchem-out FILE [--pubchem-cidcol COL]

# ChEMBL batch
harmonsmile --chembl-in FILE --chembl-out FILE [--chembl-idcol COL]

# SMILES batch
harmonsmile --smiles-in FILE --smiles-col COL --smiles-out FILE

# Single Entry
harmonsmile --pubchem-cid CID
harmonsmile --chembl-id ID
```

All batch pipelines can be combined in a single run.
Single Entry modes are mutually exclusive with their respective batch modes.

---

### Removed in v0.2.0

| Symbol | Was | Removed in |
|---|---|---|
| `Config` | Configuration dataclass for `PubChemIngest` | v0.2.0 — replaced by `PubChemConfig` |

### Still available (deprecated, will be removed in a future release)

| Symbol | Replaced by |
|---|---|
| `PubChemClient` | `_PubChemClient` (private) |

---

## Version History

| Version | Highlights |
|---|---|
| **v0.2.0** | Unified config interface — `PubChemConfig`, `ChEMBLConfig`, `SMILESConfig` replace `Config` and direct pipeline parameters (breaking change) |
| **v0.1.3** | Robustness fixes, CLI `--help` improvements, expanded test coverage, removal of deprecated coconut symbols |
| **v0.1.2** | Single Entry mode (`--pubchem-cid`, `--chembl-id`), `--smiles-*` flags, CLI test suite |
| **v0.1.1** | `RDKitStandardizer`, `PubChemIngest`, `ChEMBLIngest`, `SMILESPrep`, full CLI, PyPI release |

---

## Planned

### v0.3.0
- ECFP fingerprint generation (with/without chirality)
- InChI/InChIKey deduplication utilities
