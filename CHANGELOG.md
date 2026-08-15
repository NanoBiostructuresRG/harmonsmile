# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.3.3] - 2026-08-15

### Added
- Ruff linting configured in `pyproject.toml` (rulesets `F`, `I`, `UP`,
  `RUF022`) and enforced in CI.
- Mypy type checking configured in `pyproject.toml` and enforced in CI.
- `ruff` and `mypy` added to the `dev` optional dependency group, which
  previously did not provide the linter that `CONTRIBUTING.md` asks
  contributors to run.
- `Statement on AI Assistance` section in the README and documentation home,
  disclosing the use of generative AI tools in the development and maintenance
  of the package, in line with the pyOpenSci generative AI policy.

### Changed
- Corrected example file paths and column names across the README,
  `docs/usage.md`, and the CLI epilog: the SMILES example dataset is
  `examples/example_smiles.txt`, it is tab-delimited, and its SMILES column is
  named `SMILES`.
- Documented the ChEMBL batch CLI mode (`--chembl-in` / `--chembl-out`) in the
  README, which previously covered only the PubChem and SMILES batch modes.
- Documented the `--pubchem-cidcol` and `--chembl-idcol` options together with
  their `cid_col` and `chembl_id_col` configuration counterparts.
- Updated the Pipelines and Input Format tables to present `PubChem_CID` as the
  canonical column and to list the accepted input aliases.
- Corrected the list of supported input formats to CSV, TSV, TXT, XLSX, XLSM,
  and XLS, matching `load_table`.
- Expanded the quickstart with a statement of what it achieves, a note that the
  example datasets require cloning the repository, and links to the usage guide
  and API reference.
- Added a `to_lab_harmonized` example clarifying that it returns a
  `HarmonizationResult` rather than a string.
- Rewrote the README roadmap to reflect released versions and to state that
  fingerprint and descriptor generation are out of scope.
- `CONTRIBUTING.md`: pull requests now branch from and target `main` instead of
  the closed `dev/v0.2.4` readiness branch.
- `examples/fetch_pubchem.py` now emits the canonical `PubChem_CID` column
  instead of the legacy `PubChem CID` name.
- Applied ruff automatic fixes across the package, tests, and examples: import
  ordering, `__all__` sorting, and removal of unused and duplicated imports.
- `Callable` is now imported from `collections.abc` instead of `typing` in the
  PubChem and ChEMBL clients.
- Narrowed the `__exit__` return annotation of both HTTP clients from `bool` to
  `Literal[False]`, matching the documented behavior that exceptions are never
  suppressed.
- The CLI now uses a distinct configuration variable per pipeline instead of
  reusing a single `cfg` name across incompatible config types.
- `docs.yml` installs documentation dependencies from the `docs` extra and runs
  `mkdocs build --strict` before deploying, so broken references fail the build
  instead of being published silently.

### Removed
- `environment.yml`. RDKit was declared both there and in `pyproject.toml`;
  it is now declared once, and the contributor path is a single
  `python -m pip install -e ".[dev]"` in any Python 3.11+ environment.
- Obsolete "Future Releases (Planned)" section from this changelog, which
  described v0.3.0 as upcoming after it had been released.

### Internal
- `version.py`: version bumped to `0.3.3`.
- README project structure updated: 187 tests, `docs/` listed,
  `environment.yml` removed.

### Compatibility
- No changes to the public API surface, the output column contract, or
  harmonization behavior. The only signature change is the `__exit__` return
  annotation on two private HTTP clients, narrowed from `bool` to
  `Literal[False]` without any change in returned value. Downstream consumers
  are unaffected.

---

## [0.3.2] - 2026-07-09

### Fixed
- Made PubChem CID input detection deterministic and alias-aware.
- Changed the canonical PubChem CID output column from `PubChem CID` to `PubChem_CID`.
- Updated the PubChem example input to use `PubChem_CID`.
- Accepted common PubChem CID input aliases, including `PubChem_CID`, `PubChem CID`, `PubChemCID`, and `CID`.
- Added exact-first, normalized-fallback matching for explicit `--pubchem-cidcol` values.
- Removed ambiguous CSV delimiter sniffing for `.csv` inputs by using comma-separated loading deterministically.
- Preserved the v0.3.1 PubChem output schema with `PubChem_CID` as the canonical identifier column.

---

## [0.3.1] - 2026-07-08

### Fixed
- Refined the RDKit-native SMILES harmonization policy after v0.3.0 post-release validation.
- Preserved `SMILES_RDKit` as canonical/isomeric/Kekulé while emitting `SMILES_Harmonized` as canonical/isomeric/aromatic.
- Replaced `SMILES_Harmonization_Error` with `SMILES_Harmonization_Message`.
- Added controlled parent handling for simple salts and counterions, reporting transformations as `ok_with_warnings`.
- Prevented ambiguous multi-component or organometallic structures from being silently reduced to false `ok` outputs.
- Scoped RDKit log suppression to HARMONSMILE processing paths instead of globally silencing RDKit.
- Restored and reordered PubChem output columns, preserving source/property fields and placing `InChI`/`InChIKey` as structural bridge fields.
- Expanded the PubChem example input for post-release validation coverage.

---

## [0.3.0] - 2026-07-08

### Added
- Added an RDKit-native lab harmonization engine through `HarmonizationResult` and `RDKitStandardizer.to_lab_harmonized()`.
- Added `SMILES_Harmonized`, `SMILES_Harmonization_Status`, and `SMILES_Harmonization_Error` to `PubChemIngest`, `ChEMBLIngest`, and `SMILESPrep` outputs.
- Added typed harmonization statuses for auditable row-level results, including missing, invalid, disallowed-elements, tautomer-limit, and general harmonization-failure cases.
- Added RDKit-native MolStandardize handling for normalization, largest-fragment selection, allowed-elements validation, uncharging, reionization, tautomer canonicalization, and final canonical/isomeric/Kekulé serialization.

### Changed
- Documented the public SMILES column contract across `SMILES`, `SMILES_RDKit`, `SMILES_Harmonized`, harmonization status/error columns, and PubChem `ConnectivitySMILES`.
- Clarified that `SMILES_RDKit` remains the v0.2.5-compatible RDKit canonical/isomeric/Kekulé representation and is not a full chemical harmonization layer.
- Clarified that `SMILES_Harmonized` is intended for database harmonization, deduplication, and cross-source matching, not as a prediction of the most stable, most abundant, pH-specific, or biologically active tautomer.

### Preserved
- Preserved existing `SMILES_RDKit` behavior for compatibility with previous releases.
- Preserved PubChem `ConnectivitySMILES` as a source-specific PubChem column.
- Preserved rows when harmonization fails; failures are reported through `SMILES_Harmonization_Status` and `SMILES_Harmonization_Error`.

### Not Added
- Did not add tautomer ensemble export; `SMILES_Harmonized` stores one canonical harmonized representation per input row.

---
## [0.2.5] - 2026-07-06

### Breaking changes
- Pipeline `.run()` methods now return `pandas.DataFrame` only and no longer write output files.
- Removed `output_path` from `PubChemConfig`, `ChEMBLConfig`, and `SMILESConfig`.
- Removed unused `error_log` from pipeline configuration classes.
- Output schemas are now strict by default; use `keep_extra_columns=True` to preserve extra metadata columns.

### Changed
- CLI commands now persist outputs explicitly through `save_table(df, path)` after running the pipeline.
- `save_table()` is now the single package write boundary and validates traversal paths before creating directories.
- `environment.yml` now installs the local editable package with `-e .[dev]` instead of the obsolete `harmonsmile==0.1.0`.

### Fixed
- Prevented accidental pandas index columns such as `Unnamed: 0` and `Unnamed_0` from propagating through inputs or outputs.
- Removed the public `PubChemClient` alias while keeping `_PubChemClient` internal.
- Strengthened CI checks so editable, wheel, and sdist installs assert that `PubChemClient` is not public.

---

## [0.2.4] - 2026-06-05

### Added
- `CONTRIBUTING.md` — contribution guidelines for external contributors.
- `CODE_OF_CONDUCT.md` — community standards based on Contributor Covenant 2.1.

### Changed
- `pyproject.toml`: migrated to dynamic versioning via `hatchling` (`tool.hatch.version`).
- `pyproject.toml`: added `docs` optional dependency group with pinned versions.
- `pyproject.toml`: added `Documentation` and `Changelog` URLs.
- `pyproject.toml`: added `Operating System :: OS Independent` classifier.
- `pyproject.toml`: added SPDX header and `license-files` field.
- `README.md`: added links to `CONTRIBUTING.md` and `CODE_OF_CONDUCT.md`.
- `README.md`: clarified target users for computational chemistry,
  cheminformatics, machine learning, and data-integration workflows.
- `CONTRIBUTING.md`: expanded expectations for documentation, changelog, CI,
  PR target branch, and scientific/RDKit-related changes.
- `CODE_OF_CONDUCT.md`: added a private reporting path for conduct reports.
- `CITATION.cff`: version and release date updated for `0.2.4`.
- `CITATION.cff`: added the Zenodo DOI to match the README citation.

### Internal
- `version.py`: version bumped to `0.2.4`.
- `site/` added to `.gitignore` to prevent MkDocs build artifacts from being tracked.

---
## [0.2.3] - 2026-05-21

### Changed
- Refined the MkDocs Material documentation landing page with a custom
  HARMONSMILE hero, responsive styling, improved cards, footer social link,
  and polished pipeline tables.
- Updated `mkdocs.yml` theme settings, navigation behavior, Markdown
  extensions, custom CSS, favicon, and footer social metadata.

### Fixed
- Removed the duplicate `Changelog` heading from the documentation changelog page.
- Corrected documentation typography, spacing, badges, and table wrapping.
- Excluded `docs/` and `mkdocs.yml` from the source distribution while keeping
  them available in the repository for GitHub Pages.

### Internal
- `pyproject.toml`: version bumped to `0.2.3`.
- `version.py`: version bumped to `0.2.3`.
- `CITATION.cff`: version and release date updated for `0.2.3`.

---

## [0.2.2] - 2026-05-21

### Added
- MkDocs + Material theme + mkdocstrings documentation infrastructure.
- `docs/index.md` - home page mirroring `README.md` content.
- `docs/api.md` - auto-generated API reference from NumPy-style docstrings.
- `docs/changelog.md` - changelog page including `CHANGELOG.md` via snippets.
- `mkdocs.yml` - MkDocs configuration with Material theme, mkdocstrings
  plugin (NumPy style), and navigation structure.
- `.github/workflows/docs.yml` - new workflow that builds and deploys
  documentation to GitHub Pages on every push to `main`.
- `pyproject.toml`: new `docs` optional dependency group
  (`mkdocs-material>=9.5`, `mkdocstrings[python]>=0.25`).
- `pyproject.toml`: `Documentation` URL added under `[project.urls]`.

### Removed
- `API.md` - replaced by auto-generated `docs/api.md`.

### Internal
- `requirements-dev.txt`: documentation dependencies added.
- `version.py`: version bumped to `0.2.2`.

---

## [0.2.1] - 2026-05-20

### Changed
- `ci.yml`: Python version matrix updated to 3.11 and 3.12 (Python 3.10
  dropped - end-of-life October 2026).
- `ci.yml`: import boundary check replaced with explicit `assert` statements
  for all seven key public symbols (`PubChemConfig`, `ChEMBLConfig`,
  `SMILESConfig`, `RDKitStandardizer`, `PubChemIngest`, `ChEMBLIngest`,
  `SMILESPrep`). Same assertions applied inside the wheel smoke install step.
- `ci.yml`: removed redundant `setuptools>=68` and `wheel` from the install
  step - unnecessary with `hatchling` as the build backend.
- `ci.yml`: fixed trailing whitespace in `python -m build` line.

### Added
- `ci.yml`: new "Smoke install sdist" step - validates the `.tar.gz` source
  distribution independently from the wheel.

### Internal
- `.vscode/` removed from Git index (was previously tracked despite being
  listed in `.gitignore`).

---

## [0.2.0] - 2026-05-20

### Changed (breaking)
- `config.py`: `Config` removed and replaced by three dedicated frozen
  dataclasses - `PubChemConfig`, `ChEMBLConfig`, and `SMILESConfig` - one
  per pipeline. All three share the same validation pattern (`input_path`,
  `output_path` must not be empty or contain `..`; pipeline-specific column
  fields must not be empty or whitespace-only).
- `PubChemIngest.__init__`: now accepts `cfg: PubChemConfig` instead of
  `cfg: Config`.
- `ChEMBLIngest.__init__`: now accepts `cfg: ChEMBLConfig` instead of
  direct `input_path`, `output_path`, and `chembl_id_col` parameters.
- `SMILESPrep.__init__`: now accepts `cfg: SMILESConfig` instead of
  direct `input_path`, `smiles_col`, and `output_path` parameters.

### Added
- `PubChemConfig` - exported in `__all__`, replaces `Config` for
  `PubChemIngest`.
- `ChEMBLConfig` - new public config dataclass for `ChEMBLIngest` with
  `input_path`, `output_path`, `chembl_id_col`, and `error_log` fields.
- `SMILESConfig` - new public config dataclass for `SMILESPrep` with
  `input_path`, `output_path`, `smiles_col`, and `error_log` fields.

### Docs
- `__init__.py`: module docstring updated - classes section and all
  examples reflect the new config classes.
- `__main__.py`: docstring examples updated; removed stale `--coconut-*`
  example that survived from v0.1.2.
- `pipelines.py`: all three pipeline docstrings updated with new config
  types and examples.
- `API.md`: updated to v0.2.0 - `Config` removed, three new config classes
  documented with full parameter and validation tables.
- `README.md`: all Python API examples updated to use new config classes;
  version badge bumped to v0.2.0.

### Tests
- `test_config.py`: `TestConfig` renamed to `TestPubChemConfig`;
  `TestChEMBLConfig` and `TestSMILESConfig` added (10 cases each).
- `test_pipelines.py`: all pipeline instantiation updated to use new
  config classes.
- `test_security.py`: `TestConfigSecurity` renamed to
  `TestPubChemConfigSecurity`; `TestChEMBLConfigSecurity` and
  `TestSMILESConfigSecurity` added.
- `test_cli.py`: batch ChEMBL and SMILES tests updated to read paths
  from config object instead of kwargs.
- **Final count:** 146 tests passing (+27 net vs v0.1.3).

### Internal
- `_cli.py`: internal instantiation updated to use `PubChemConfig`,
  `ChEMBLConfig`, and `SMILESConfig`.
- `version.py`: version bumped to `0.2.0`.

---

## [0.1.3] - 2026-05-19

### Changed
- `_cli.py`: removed deprecated `--coconut-in`, `--coconut-out`, and
  `--coconut-smiles` flags and their migration logic. These aliases were
  introduced in v0.1.2 as a compatibility bridge; use `--smiles-in`,
  `--smiles-out`, and `--smiles-col` instead.
- `pipelines.py`: removed `CoconutPrep` deprecated alias for `SMILESPrep`.
- `__init__.py`: removed `CoconutPrep` from imports and `__all__`.

### Fixed
- `config.py`: `Config.__post_init__` now raises `ValueError` when `cid_col`
  is an empty or whitespace-only string.
- `config.py`: `Config.__post_init__` now rejects `input_path` values
  containing `..` (path traversal), consistent with the existing check on
  `output_path`.
- `io.py`: `load_table` now raises `FileNotFoundError` with a descriptive
  message when the input file does not exist, instead of propagating a raw
  pandas or OS error.
- `io.py`: `load_table` now raises `ValueError` when the loaded DataFrame
  has zero rows.
- `io.py`: `_sanitize_cid` no longer raises on unexpected input types
  (`bool`, `list`, `dict`, etc.); the `pd.isna()` call is now wrapped in a
  try/except.
- `pipelines.py`: `PubChemIngest.run()`, `ChEMBLIngest.run()`, and
  `SMILESPrep.run()` now raise `ValueError` early when the input DataFrame
  is empty, instead of silently producing an empty output file.
- `pipelines.py`: `PubChemIngest.run()` now emits a `logger.warning` when
  the `SMILES` column is absent after fetching, making the silent omission
  of `SMILES_RDKit` visible.
- `pipelines.py`: `SMILESPrep.run()` now creates output directories only
  after `load_table` succeeds, avoiding the creation of empty directories
  when the input file does not exist.

### Improved
- `_cli.py`: `--help` output now includes a concrete usage epilog with
  examples for every pipeline (PubChem batch, ChEMBL batch, SMILES batch,
  single-entry CID, single-entry ChEMBL ID, multi-pipeline call).
- `_cli.py`: the "nothing to run" error message now lists all valid flag
  combinations and includes usage examples.

### Docs
- `config.py`: `Config` docstring updated to document new `cid_col` and
  `input_path` validation in the `Raises` section.
- `io.load_table`: `Raises` section updated to document `FileNotFoundError`
  and empty-DataFrame `ValueError`.
- `io.save_table`: documented the automatic creation of missing parent
  directories.
- `pipelines.PubChemIngest.run()`, `ChEMBLIngest.run()`, `SMILESPrep.run()`:
  `Raises` sections updated to document empty-DataFrame `ValueError`.

### Tests
- Added 14 new test cases and removed 4 obsolete ones (deprecated coconut
  CLI aliases), for a net total of 119 tests (+10 vs v0.1.2).
- New cases cover: `Config` validation (`cid_col` empty or whitespace,
  `input_path` path traversal), `_sanitize_cid` edge types (`bool`, `list`,
  `dict`), `load_table` error paths (nonexistent file, empty file),
  empty-DataFrame guards in all three pipelines, missing-`SMILES`-column
  warning in `PubChemIngest`, and a new `test_pipelines.py` module.

---

## [0.1.2] - 2026-05-18

### Added
- CLI: Single Entry mode - `harmonsmile --pubchem-cid <CID>` and
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
- CLI help groups renamed: `"COCONUT / independent"` -> `"SMILES (batch)"`;
  `"PubChem"` -> `"PubChem (batch)"`; `"ChEMBL"` -> `"ChEMBL (batch)"`.
- `API.md` formalized with complete reference for all public classes and methods.

### Fixed
- `ChEMBLIngest`: duplicate `name` column in output when input file already
  contained a `name` column and ChEMBL API returned `pref_name`.

### Docs
- `RDKitStandardizer.to_iso_kek()`: added Notes section documenting E/Z
  geometry behavior - chiral centers are preserved; E/Z on double bonds may
  be lost for ambiguous cases during kekulization (known RDKit behavior).

---

## [0.1.1] - 2026-05-18

### Added
- `RDKitStandardizer` class with two SMILES normalization methods:
  - `to_iso_kek()` - canonical + isomeric + Kekulized SMILES (COCONUT 2.0 convention)
  - `to_conn_kek()` - canonical + connectivity-only + Kekulized SMILES
- `PubChemIngest` pipeline: fetches all available properties from PubChem REST API
  (SMILES, ConnectivitySMILES, MolecularWeight, MolecularFormula, InChI, InChIKey,
  XLogP, TPSA, Charge, HBondDonorCount, HBondAcceptorCount, RotatableBondCount,
  HeavyAtomCount) and appends standardized `SMILES_RDKit` column.
- `ChEMBLIngest` pipeline: fetches properties from ChEMBL REST API by ChEMBL ID
  (canonical_smiles, InChI, InChIKey, MW, MolecularFormula, ALogP, TPSA, HBA, HBD,
  RotatableBonds, HeavyAtoms, QED, Ro5Violations) and appends standardized `SMILES_RDKit` column.
- `SMILESPrep` pipeline: standardizes SMILES from any CSV/Excel file using RDKit -
  accepts any tabular source (COCONUT, ChEMBL downloads, in-house databases, etc.).
- `_PubChemClient` with configurable retries, exponential backoff, persistent
  `requests.Session`, context manager protocol, and pluggable logger.
- `_ChEMBLClient` with same design as `_PubChemClient` - ChEMBL ID format validation,
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
- `_PubChemClient`: bounds validation on `sleep` (0.1-10.0 s) and `retries` (1-10).
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

[0.3.3]: https://github.com/NanoBiostructuresRG/harmonsmile/compare/v0.3.2...v0.3.3
[0.3.2]: https://github.com/NanoBiostructuresRG/harmonsmile/compare/v0.3.1...v0.3.2
[0.3.1]: https://github.com/NanoBiostructuresRG/harmonsmile/compare/v0.3.0...v0.3.1
[0.3.0]: https://github.com/NanoBiostructuresRG/harmonsmile/compare/v0.2.5...v0.3.0
[0.2.5]: https://github.com/NanoBiostructuresRG/harmonsmile/compare/v0.2.4...v0.2.5
[0.2.4]: https://github.com/NanoBiostructuresRG/harmonsmile/compare/v0.2.3...v0.2.4
[0.2.3]: https://github.com/NanoBiostructuresRG/harmonsmile/compare/v0.2.2...v0.2.3
[0.2.2]: https://github.com/NanoBiostructuresRG/harmonsmile/compare/v0.2.1...v0.2.2
[0.2.1]: https://github.com/NanoBiostructuresRG/harmonsmile/compare/v0.2.0...v0.2.1
[0.2.0]: https://github.com/NanoBiostructuresRG/harmonsmile/compare/v0.1.3...v0.2.0
[0.1.3]: https://github.com/NanoBiostructuresRG/harmonsmile/compare/v0.1.2...v0.1.3
[0.1.2]: https://github.com/NanoBiostructuresRG/harmonsmile/compare/v0.1.1...v0.1.2
[0.1.1]: https://github.com/NanoBiostructuresRG/harmonsmile/releases/tag/v0.1.1
[0.1.0]: https://github.com/NanoBiostructuresRG/harmonsmile/releases/tag/v0.1.0
