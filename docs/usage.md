# Usage

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
