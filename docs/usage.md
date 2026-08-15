# Usage

## Installation

### For package users

Create and activate a Python environment, then install from PyPI:

```bash
conda create -n harmonsmile_env python=3.11
conda activate harmonsmile_env
pip install harmonsmile
```

RDKit (`rdkit>=2022.09`) is a required runtime dependency and is installed
automatically as part of the package dependencies.

### For contributors and developers

```bash
git clone https://github.com/NanoBiostructuresRG/harmonsmile.git
cd harmonsmile
conda create -n harmonsmile_env python=3.11
conda activate harmonsmile_env
python -m pip install -e ".[dev]"
```

To build these docs locally, add the `docs` extra:

```bash
python -m pip install -e ".[dev,docs]"
mkdocs serve
```

## Quick Start

Each pipeline reads an input table, resolves and harmonizes structures, and
returns a `pandas.DataFrame` carrying the SMILES column contract. Nothing is
written to disk until you call `save_table`.

!!! note "Example data"

    The snippets below use the datasets in `examples/`, which ship with the
    repository but not with the PyPI wheel. To run them as written, clone the
    repository and work from its root:

    ```bash
    git clone https://github.com/NanoBiostructuresRG/harmonsmile.git
    cd harmonsmile
    ```

    To use your own data instead, point `input_path` at any CSV, TSV, TXT,
    XLSX, XLSM, or XLS file with the columns listed under
    [Input Format](#input-format).

=== "PubChem"

    ```python
    from harmonsmile import PubChemIngest, PubChemConfig, save_table

    cfg = PubChemConfig(
        input_path="examples/example_pubchem.csv",   # columns: id, PubChem_CID
    )
    df = PubChemIngest(cfg).run()
    save_table(df, "results/example_pubchem_harmonized.csv")
    ```

    `PubChem_CID` is the canonical input column. `PubChem CID`, `PubChemCID`,
    and `CID` are accepted as aliases. For any other name, pass
    `cid_col="your_column"`.

=== "ChEMBL"

    ```python
    from harmonsmile import ChEMBLIngest, ChEMBLConfig, save_table

    cfg = ChEMBLConfig(
        input_path="examples/example_chembl.csv",    # columns: id, ChEMBL ID
    )
    df = ChEMBLIngest(cfg).run()
    save_table(df, "results/example_chembl_harmonized.csv")
    ```

    The identifier column defaults to `ChEMBL ID`. Override it with
    `chembl_id_col="your_column"`.

=== "SMILES"

    ```python
    from harmonsmile import SMILESPrep, SMILESConfig, save_table

    cfg = SMILESConfig(
        input_path="examples/example_smiles.txt",    # columns: id, name, SMILES
        smiles_col="SMILES",
    )
    df = SMILESPrep(cfg).run()
    save_table(df, "results/example_smiles_harmonized.csv")
    ```

    The example file is tab-delimited. The SMILES column may carry any name;
    declare it through `smiles_col`.

=== "Single SMILES"

    ```python
    from harmonsmile import RDKitStandardizer

    std = RDKitStandardizer()
    print(std.to_iso_kek("c1ccccc1"))    # 'C1=CC=CC=C1'  canonical + isomeric + Kekulized
    print(std.to_conn_kek("c1ccccc1"))   # 'C1=CC=CC=C1'  connectivity only, no stereochemistry

    result = std.to_lab_harmonized("c1ccccc1")
    print(result.value)                  # 'c1ccccc1'     lab-harmonized, aromatic
    print(result.status)                 # 'ok'
    ```

    `to_lab_harmonized` returns a `HarmonizationResult` with `value`, `status`,
    `error`, and `warning` fields, not a bare string.

## Command-Line Interface

```bash
# PubChem batch
harmonsmile --pubchem-in  examples/example_pubchem.csv \
            --pubchem-out results/example_pubchem_harmonized.csv

# ChEMBL batch
harmonsmile --chembl-in  examples/example_chembl.csv \
            --chembl-out results/example_chembl_harmonized.csv

# SMILES batch
harmonsmile --smiles-in  examples/example_smiles.txt --smiles-col SMILES \
            --smiles-out results/example_smiles_harmonized.csv

# Single entry - output written to results/ automatically
harmonsmile --pubchem-cid 2723949
harmonsmile --chembl-id CHEMBL294199
```

Non-standard identifier column names are declared explicitly:

```bash
harmonsmile --pubchem-in  data/my_table.csv --pubchem-cidcol "compound_cid" \
            --pubchem-out results/out.csv

harmonsmile --chembl-in  data/my_table.csv --chembl-idcol "chembl_identifier" \
            --chembl-out results/out.csv
```

Batch arguments are paired: `--*-in` requires its matching `--*-out`, and
`--smiles-in` additionally requires `--smiles-col`. Single-entry and batch mode
for the same source are mutually exclusive.

Run `harmonsmile --help` for the full argument reference.

## Pipelines

<div class="hs-grid hs-grid--three">
  <article class="hs-card hs-card--compact">
    <h3>PubChem</h3>
    <p><code>PubChemIngest</code> reads a table with a <code>PubChem_CID</code> column and resolves molecules through the public REST API.</p>
  </article>

  <article class="hs-card hs-card--compact">
    <h3>ChEMBL</h3>
    <p><code>ChEMBLIngest</code> reads a table with a <code>ChEMBL ID</code> column and resolves structures through the public REST API.</p>
  </article>

  <article class="hs-card hs-card--compact">
    <h3>Local SMILES</h3>
    <p><code>SMILESPrep</code> accepts delimited or Excel files with any SMILES column name and processes them locally.</p>
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
      <td>Table with a <code>PubChem_CID</code> column</td>
      <td>REST (public)</td>
    </tr>
    <tr>
      <td><code>ChEMBLIngest</code></td>
      <td><code>ChEMBLConfig</code></td>
      <td>ChEMBL</td>
      <td>Table with a <code>ChEMBL ID</code> column</td>
      <td>REST (public)</td>
    </tr>
    <tr>
      <td><code>SMILESPrep</code></td>
      <td><code>SMILESConfig</code></td>
      <td>Any</td>
      <td>Table with any SMILES column</td>
      <td>Local file</td>
    </tr>
  </tbody>
</table>

All pipelines preserve source `SMILES`, append compatibility `SMILES_RDKit`,
and append `SMILES_Harmonized`, `SMILES_Harmonization_Status`, and
`SMILES_Harmonization_Message`.
Pipeline `.run()` methods return a `pandas.DataFrame` and do not write files.
Use `save_table(df, path)` from Python, or the CLI `--*-out` options, to
persist results.

## Input Format

| Pipeline | Required columns | Column option |
|---|---|---|
| `PubChemIngest` | `id` (optional), `PubChem_CID` | `cid_col` / `--pubchem-cidcol` |
| `ChEMBLIngest` | `id` (optional), `ChEMBL ID` | `chembl_id_col` / `--chembl-idcol` |
| `SMILESPrep` | `id` (optional), `<smiles_col>` (any name) | `smiles_col` / `--smiles-col` |

`PubChemIngest` accepts `PubChem_CID` (canonical), `PubChem CID`, `PubChemCID`,
and `CID` as input aliases, and always emits `PubChem_CID` in the output.

Supported file formats: CSV, TSV, TXT, XLSX, XLSM, XLS. `.csv` is read as
comma-delimited and `.tsv` / `.txt` as tab-delimited, deterministically and
without delimiter sniffing.

## Next steps

- [API reference](api.md) — full signatures for every public class and function.
- `examples/fetch_pubchem.py` and `examples/fetch_chembl.py` — build larger
  input tables from a free-text query before running a pipeline.
