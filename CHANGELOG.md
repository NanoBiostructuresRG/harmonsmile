# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

---

## [0.1.0] - 2025-09-19

### Added
- `RDKitStandardizer` class with two SMILES normalization methods:
  - `to_iso_kek()` — canonical + isomeric + Kekulized SMILES (COCONUT 2.0 convention)
  - `to_conn_kek()` — canonical + connectivity-only + Kekulized SMILES
- `PubChemIngest` pipeline: fetches properties (SMILES, MolecularWeight) from PubChem REST API
  and appends standardized `SMILES_RDKit` column.
- `CoconutPrep` pipeline: standardizes SMILES from any CSV/Excel file using RDKit.
- `PubChemClient` with configurable retries, exponential backoff, persistent `requests.Session`,
  and pluggable logger.
- `Config` frozen dataclass for pipeline configuration with `__post_init__` validation.
- `load_table()` and `save_table()` I/O utilities supporting CSV, TSV, XLSX, and XLS formats,
  with `PathLike` support.
- Command-line interface via `harmonsmile` entry point and `python -m harmonsmile`,
  with paired argument validation and grouped help output.
- `pyproject.toml` for PyPI packaging (build backend: hatchling).
- SPDX license headers (`LGPL-3.0-or-later`) in all source files.
- NumPy-style docstrings with Examples in all public modules and classes.
- `CITATION.cff` for software citation.
- `CHANGELOG.md` following Keep a Changelog format.

### Security
- `PubChemClient`: bounds validation on `sleep` (0.1–10.0 s) and `retries` (1–10).
- `PubChemClient.fetch_props()`: CID sanitization strips non-numeric characters before URL construction.
- `Config`: path traversal guard rejects `output_path` containing `..`.
- `Config`: `VALID_PUBCHEM_PROPS` allowlist validates requested PubChem properties.

### Changed
- License changed from MIT to GNU Lesser General Public License v3.0 or later (LGPL-3.0-or-later).
- `__main__.py` now delegates to `harmonsmile._cli` instead of `cli.harmonize`,
  making the package self-contained and installable from PyPI.
- `CoconutPrep.run()` now uses `load_table()` for consistent format support across pipelines.
- Console status messages changed to English for international audience.
- `Config` is now immutable (`frozen=True`).
- `CoconutPrep` renamed to `SMILESPrep` to reflect its universal scope — accepts any tabular file with a SMILES column, not only COCONUT databases. `CoconutPrep` remains available as a deprecated alias and will be removed in a future release.
- `PubChemClient` renamed to `_PubChemClient` (private) to prevent direct use 
  that could abuse the PubChem REST API. `PubChemClient` remains available as a 
  deprecated alias and will be removed in a future release.

### Fixed
- Double `time.sleep()` call in `PubChemClient.fetch_props()` that caused unnecessary delays
  on successful requests.
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
- Unused module-level logger in `pubchem.py`.

---

## Future Releases (Planned)

### [0.2.0] — ChEMBL source
- Add `ChEMBLIngest` pipeline with the same RDKit normalization → unified `SMILES_RDKit` output.

### [0.3.0] — ML-ready features
- Standardized pipeline to generate ECFP fingerprints (with/without chirality).
- InChI / InChIKey generation for deduplication and robust cross-database matching.

---

[Unreleased]: https://github.com/NanoBiostructuresRG/harmonsmile/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/NanoBiostructuresRG/harmonsmile/releases/tag/v0.1.0
