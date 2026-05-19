# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.1.2] - 2026-05-18

### Added
- CLI: Single Entry mode — `harmonsmile --pubchem-cid <CID>` and
  `harmonsmile --chembl-id <ID>` fetch and harmonize a single compound
  without an input file. Output saved automatically to
  `results/CID{cid}_harmonsmile.csv` and `results/{id}_harmonsmile.csv`.
- `examples/` directory with real-world fetch scripts and capsaicin datasets
  for PubChem, ChEMBL, and SMILES batch modes.
- Unit tests for CLI (`test_cli.py`, 32 tests) covering batch modes,
  single entry modes, deprecated aliases, mutual exclusion, and validation.

### Changed
- CLI: `--coconut-in`, `--coconut-out`, `--coconut-smiles` renamed to
  `--smiles-in`, `--smiles-out`, `--smiles-col` for source-agnostic naming.
  Deprecated aliases kept with `DeprecationWarning`.
- CLI help groups renamed: `"COCONUT / independent"` → `"SMILES (batch)"`;
  `"PubChem"` → `"PubChem (batch)"`; `"ChEMBL"` → `"ChEMBL (batch)"`.
- `API.md` formalized with complete reference for all public classes and methods.

### Fixed
- `ChEMBLIngest`: duplicate `name` column in output when input file already
  contained a `name` column and ChEMBL API returned `pref_name`.

### Docs
- `RDKitStandardizer.to_iso_kek()`: added Notes section documenting E/Z
  geometry behavior — chiral centers are preserved; E/Z on double bonds may
  be lost for ambiguous cases during kekulization (known RDKit behavior).

---

## [0.1.1] - 2026-05-18

### Added
- `RDKitStandardizer` class with two SMILES normalization methods:
  - `to_iso_kek()` — canonical + isomeric + Kekulized SMILES (COCONUT 2.0 convention)
  - `to_conn_kek()` — canonical + connectivity-only + Kekulized SMILES
- `PubChemIngest` pipeline: fetches all available properties from PubChem REST API
  (SMILES, ConnectivitySMILES, MolecularWeight, MolecularFormula, InChI, InChIKey,
  XLogP, TPSA, Charge, HBondDonorCount, HBondAcceptorCount, RotatableBondCount,
  HeavyAtomCount) and appends standardized `SMILES_RDKit` column.
- `ChEMBLIngest` pipeline: fetches properties from ChEMBL REST API by ChEMBL ID
  (canonical_smiles, InChI, InChIKey, MW, MolecularFormula, ALogP, TPSA, HBA, HBD,
  RotatableBonds, HeavyAtoms, QED, Ro5Violations) and appends standardized `SMILES_RDKit` column.
- `SMILESPrep` pipeline: standardizes SMILES from any CSV/Excel file using RDKit —
  accepts any tabular source (COCONUT, ChEMBL downloads, in-house databases, etc.).
- `_PubChemClient` with configurable retries, exponential backoff, persistent
  `requests.Session`, context manager protocol, and pluggable logger.
- `_ChEMBLClient` with same design as `_PubChemClient` — ChEMBL ID format validation,
  exponential backoff, context manager protocol.
- `Config` frozen dataclass for pipeline configuration with `__post_init__` validation.
- `load_table()` and `save_table()` I/O utilities supporting CSV, TSV, XLSX, and XLS
  formats, with `PathLike` support.
- `version.py` as single source of truth for package metadata (`__version__`,
  `PROJECT_NAME`, `PROJECT_VERSION`, `PROJECT_STATUS`).
- Command-line interface via `harmonsmile` entry point and `python -m harmonsmile`,
  with paired argument validation, grouped help output, and `--version` flag.
- `pyproject.toml` for PyPI packaging (build backend: hatchling).
- SPDX license headers (`LGPL-3.0-or-later`) in all source files.
- NumPy-style docstrings with Examples in all public modules and classes.
- `CITATION.cff` for software citation.
- `CHANGELOG.md` following Keep a Changelog format.
- `environment.yml` and `requirements-dev.txt` for reproducible environments.
- Unit test suite with pytest covering standardize, config, io,
  pubchem, chembl, and security.

### Security
- `_PubChemClient`: bounds validation on `sleep` (0.1–10.0 s) and `retries` (1–10).
- `_PubChemClient.fetch_props()`: CID sanitization strips non-numeric characters
  before URL construction.
- `_ChEMBLClient`: same bounds validation; ChEMBL ID format validated against
  `^CHEMBL\d+$` regex before network calls.
- `Config`: path traversal guard rejects `output_path` containing `..`.
- `Config`: `VALID_PUBCHEM_PROPS` allowlist validates requested PubChem properties.

### Changed
- License changed from MIT to GNU Lesser General Public License v3.0 or later
  (LGPL-3.0-or-later).
- `__main__.py` now delegates to `harmonsmile._cli` instead of `cli.harmonize`,
  making the package self-contained and installable from PyPI.
- Console status messages changed to English for international audience.
- `Config` is now immutable (`frozen=True`).
- `CoconutPrep` renamed to `SMILESPrep` to reflect its universal scope. `CoconutPrep`
  remains available as a deprecated alias and will be removed in a future release.
- `PubChemClient` renamed to `_PubChemClient` (private) to prevent direct use that
  could abuse the PubChem REST API. `PubChemClient` remains available as a deprecated
  alias and will be removed in a future release.
- Default `props` in `Config` expanded to include all available PubChem properties.
- Development status set to Alpha (`3 - Alpha`) reflecting first public release.

### Fixed
- Double `time.sleep()` call in `_PubChemClient.fetch_props()` that caused unnecessary
  delays on successful requests.
- Missing column validation in `PubChemIngest.run()` before initiating network calls.
- Incorrect guard condition for `SMILES_RDKit` counter in `PubChemIngest.run()`.
- Unguarded `Chem.MolToSmiles()` call in `RDKitStandardizer` that could raise unhandled
  C++ exceptions for unusual aromaticity models.
- Fallback encoding in `load_table()` changed to `latin-1` to correctly handle
  non-UTF-8 encoded files.

### Removed
- Redundant `cli/` scripts (`harmonize.py`, `ingest_pubchem.py`, `prep_coconut.py`)
  superseded by the unified `harmonsmile` entry point.
- Unused `id_col` field from `Config` dataclass.

---

## Future Releases (Planned)

### [0.2.0] — COCONUT source
- Add `CoconutIngest` pipeline — knows COCONUT 2.0 schema automatically
  (`canonical_smiles` column, `identifier`, molecular properties).
- Optional COCONUT REST API integration (authenticated).

### [0.3.0] — ML-ready features
- Standardized pipeline to generate ECFP fingerprints (with/without chirality).
- InChI / InChIKey generation for deduplication and robust cross-database matching.

---

[0.1.2]: https://github.com/NanoBiostructuresRG/harmonsmile/compare/v0.1.1...v0.1.2
[0.1.1]: https://github.com/NanoBiostructuresRG/harmonsmile/releases/tag/v0.1.1
[0.1.0]: https://github.com/NanoBiostructuresRG/harmonsmile/releases/tag/v0.1.0