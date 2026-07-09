# Usage

## Installation

### For package users:

Create and activate a Python environment:

```bash
conda create -n harmonsmile_env python=3.11
conda activate harmonsmile_env
```

Install **HARMONSMILE** from PyPI:

```bash
pip install harmonsmile
```


### For contributors/developers:

Clone the repository:

```bash
git clone https://github.com/NanoBiostructuresRG/harmonsmile.git
cd harmonsmile
```

Create and activate the development environment:

```bash
conda env create -f environment.yml
conda activate harmonsmile_env
```

Install HARMONSMILE in editable mode with development dependencies:

```bash
python -m pip install -e .[dev]
```

> RDKit is a required runtime dependency (`rdkit>=2022.09`). For package users, it is declared in `pyproject.toml` and installed through the package dependency resolver. For contributors, `environment.yml` preinstalls RDKit from `conda-forge` for a stable local scientific stack.

## Quick Start

=== "PubChem"

    ```python
    from harmonsmile import PubChemIngest, PubChemConfig, save_table

    cfg = PubChemConfig(
        input_path="examples/example_pubchem.csv",
    )
    df = PubChemIngest(cfg).run()
    save_table(df, "results/example_pubchem_harmonized.csv")
    ```

=== "ChEMBL"

    ```python
    from harmonsmile import ChEMBLIngest, ChEMBLConfig, save_table

    cfg = ChEMBLConfig(
        input_path="examples/example_chembl.csv",
    )
    df = ChEMBLIngest(cfg).run()
    save_table(df, "results/example_chembl_harmonized.csv")
    ```

=== "SMILES"

    ```python
    from harmonsmile import SMILESPrep, SMILESConfig, save_table

    cfg = SMILESConfig(
        input_path="examples/example_smiles.csv",
        smiles_col="SMILES",
    )
    df = SMILESPrep(cfg).run()
    save_table(df, "results/example_smiles_harmonized.csv")
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

All pipelines preserve source `SMILES`, append compatibility `SMILES_RDKit`,
and append `SMILES_Harmonized`, `SMILES_Harmonization_Status`, and
`SMILES_Harmonization_Message`.
Pipeline `.run()` methods return a `pandas.DataFrame` and do not write files.
Use `save_table(df, path)` from Python, or CLI `--*-out` options, to persist
results.

## Input Format

| Pipeline | Required columns |
|---|---|
| `PubChemIngest` | `id` (optional), `PubChem CID` |
| `ChEMBLIngest` | `id` (optional), `ChEMBL ID` |
| `SMILESPrep` | `id` (optional), `<smiles_col>` (any name) |

Supported file formats: CSV, TSV, XLSX, XLS.
