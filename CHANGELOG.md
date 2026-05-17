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
- `PubChemClient` with configurable retries, exponential backoff, and pluggable logger.
- `Config` dataclass for pipeline configuration.
- `load_table()` and `save_table()` I/O utilities supporting CSV, TSV, XLSX, and XLS formats.
- Command-line interface via `harmonsmile` entry point and `python -m harmonsmile`.
- `pyproject.toml` for PyPI packaging (build backend: hatchling).

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
