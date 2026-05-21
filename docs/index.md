# HARMONSMILE

<section class="hs-hero">
  <div class="hs-hero__content">
    <p class="hs-eyebrow">Cheminformatics data preparation</p>
    <div class="hs-brand" aria-label="HARMONSMILE">
      <span class="hs-dotmark" aria-hidden="true">
        <span></span><span></span><span></span>
        <span></span><span></span><span></span>
        <span></span><span></span><span></span>
      </span>
      <span class="hs-wordmark">HARMONSMILE</span>
    </div>
    <p class="hs-subtitle">Harmonize SMILES strings for reproducible cheminformatics and machine learning workflows.</p>

    <div class="hs-actions">
      <a class="md-button md-button--primary" href="#installation">Install</a>
      <a class="md-button" href="#quick-start">Quick start</a>
      <a class="md-button" href="api/">API Reference</a>
    </div>

    <div class="hs-badges">
      <a href="https://github.com/NanoBiostructuresRG/harmonsmile/actions/workflows/ci.yml"><img src="https://github.com/NanoBiostructuresRG/harmonsmile/actions/workflows/ci.yml/badge.svg" alt="CI"></a>
      <a href="https://pypi.org/project/harmonsmile/"><img src="https://img.shields.io/pypi/v/harmonsmile.svg" alt="PyPI"></a>
      <a href="https://pypi.org/project/harmonsmile/"><img src="https://img.shields.io/pypi/pyversions/harmonsmile.svg" alt="Python versions"></a>
      <a href="https://github.com/NanoBiostructuresRG/harmonsmile/blob/main/LICENSE"><img src="https://img.shields.io/badge/License-LGPL_v3-blue.svg" alt="License: LGPL v3"></a>
    </div>
  </div>
</section>

<section class="hs-panel">
  <div class="hs-grid hs-grid--three">
    <article class="hs-card">
      <span class="hs-card__icon">DB</span>
      <h3>Normalize datasets</h3>
      <p>Standardize SMILES from PubChem, ChEMBL, COCONUT, and in-house collections.</p>
    </article>

    <article class="hs-card">
      <span class="hs-card__icon">RD</span>
      <h3>RDKit convention</h3>
      <p>Generate canonical, isomeric, Kekulized representations for consistent comparison.</p>
    </article>

    <article class="hs-card">
      <span class="hs-card__icon">ML</span>
      <h3>ML-ready outputs</h3>
      <p>Append harmonized columns that are easier to deduplicate, compare, and model.</p>
    </article>
  </div>
</section>

## Why HARMONSMILE?

The same molecule can arrive with different SMILES strings depending on the source.
That inconsistency complicates comparisons, deduplication, and machine learning
pipelines that expect a uniform molecular representation.

**HARMONSMILE** automates molecular dataset preparation for cheminformatics workflows
and **phase 1** machine learning applications within computational drug discovery.

!!! tip "Core harmonization"
    HARMONSMILE standardizes SMILES to a consistent **canonical + isomeric + Kekulized**
    representation using the RDKit convention widely adopted by the cheminformatics
    community.

## Installation

```bash
pip install harmonsmile
```

> RDKit is required and installed automatically (`rdkit>=2022.09`).

## Quick Start

=== "PubChem"

    ```python
    from harmonsmile import PubChemIngest, PubChemConfig

    cfg = PubChemConfig(
        input_path="examples/example_pubchem.csv",
        output_path="results/example_pubchem_harmonized.csv",
    )
    PubChemIngest(cfg).run()
    ```

=== "ChEMBL"

    ```python
    from harmonsmile import ChEMBLIngest, ChEMBLConfig

    cfg = ChEMBLConfig(
        input_path="examples/example_chembl.csv",
        output_path="results/example_chembl_harmonized.csv",
    )
    ChEMBLIngest(cfg).run()
    ```

=== "SMILES"

    ```python
    from harmonsmile import SMILESPrep, SMILESConfig

    cfg = SMILESConfig(
        input_path="examples/example_smiles.csv",
        smiles_col="SMILES",
        output_path="results/example_smiles_harmonized.csv",
    )
    SMILESPrep(cfg).run()
    ```

=== "Single SMILES"

    ```python
    from harmonsmile import RDKitStandardizer

    std = RDKitStandardizer()
    print(std.to_iso_kek("c1ccccc1"))    # canonical + isomeric + Kekulized
    print(std.to_conn_kek("c1ccccc1"))   # canonical + connectivity-only + Kekulized
    ```

## Command-Line Interface

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
```

## Pipelines

<div class="hs-grid hs-grid--three">
  <article class="hs-card hs-card--compact">
    <h3>PubChem</h3>
    <p><code>PubChemIngest</code> reads CSV data with a <code>PubChem CID</code> column and resolves molecules through the public REST API.</p>
  </article>

  <article class="hs-card hs-card--compact">
    <h3>ChEMBL</h3>
    <p><code>ChEMBLIngest</code> reads CSV data with a <code>ChEMBL ID</code> column and resolves structures through the public REST API.</p>
  </article>

  <article class="hs-card hs-card--compact">
    <h3>Local SMILES</h3>
    <p><code>SMILESPrep</code> accepts CSV or Excel files with any SMILES column name and processes them locally.</p>
  </article>
</div>

<table class="hs-pipeline-table">
  <thead>
    <tr>
      <th>Pipeline</th>
      <th>Config</th>
      <th>Source</th>
      <th>Input</th>
      <th>API</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><code>PubChemIngest</code></td>
      <td><code>PubChemConfig</code></td>
      <td>PubChem</td>
      <td>CSV with <code>PubChem CID</code> column</td>
      <td>REST (public)</td>
    </tr>
    <tr>
      <td><code>ChEMBLIngest</code></td>
      <td><code>ChEMBLConfig</code></td>
      <td>ChEMBL</td>
      <td>CSV with <code>ChEMBL ID</code> column</td>
      <td>REST (public)</td>
    </tr>
    <tr>
      <td><code>SMILESPrep</code></td>
      <td><code>SMILESConfig</code></td>
      <td>Any</td>
      <td>CSV/Excel with any SMILES column</td>
      <td>Local file</td>
    </tr>
  </tbody>
</table>

All pipelines append a `SMILES_RDKit` column with the harmonized SMILES.

## Input Format

| Pipeline | Required columns |
|---|---|
| `PubChemIngest` | `id` (optional), `PubChem CID` |
| `ChEMBLIngest` | `id` (optional), `ChEMBL ID` |
| `SMILESPrep` | `id` (optional), `<smiles_col>` (any name) |

Supported file formats: CSV, TSV, XLSX, XLS.

## Citation

```text
Contreras-Torres, F. F. (2026). HARMONSMILE: Harmonize SMILES Strings for Cheminformatics and Machine Learning (v0.2.2).
Zenodo. https://doi.org/10.5281/zenodo.20321584
```

## License

This project is licensed under the terms of the
[GNU Lesser General Public License v3.0 or later](https://github.com/NanoBiostructuresRG/harmonsmile/blob/main/LICENSE).
SPDX identifier: `LGPL-3.0-or-later`.
