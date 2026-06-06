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
    <p class="hs-subtitle">Harmonize SMILES strings for reproducible molecular dataset preparation.</p>

    <div class="hs-actions">
      <a class="md-button md-button--primary" href="usage/#installation">Install</a>
      <a class="md-button" href="usage/#quick-start">Quick start</a>
      <a class="md-button" href="api/">API Reference</a>
      <a class="md-button" href="changelog/">Changelog</a>
    </div>

    <div class="hs-badges">
      <a href="https://github.com/NanoBiostructuresRG/harmonsmile/actions/workflows/ci.yml"><img src="https://github.com/NanoBiostructuresRG/harmonsmile/actions/workflows/ci.yml/badge.svg" alt="CI"></a>
      <a href="https://pypi.org/project/harmonsmile/"><img src="https://img.shields.io/pypi/v/harmonsmile.svg" alt="PyPI"></a>
      <a href="https://pypi.org/project/harmonsmile/"><img src="https://img.shields.io/pypi/pyversions/harmonsmile.svg" alt="Python versions"></a>
      <a href="https://github.com/NanoBiostructuresRG/harmonsmile/blob/main/LICENSE"><img src="https://img.shields.io/badge/License-LGPL_v3-blue.svg" alt="License: LGPL v3"></a>
    </div>
  </div>
</section>


## Why SMILES harmonization matters

Molecular datasets are often assembled from multiple sources: PubChem records, ChEMBL bioactivity tables, natural product collections such as COCONUT, and local or in-house compound lists. In these settings, the SMILES column is frequently used as the practical key for comparison, merging, deduplication, and downstream feature generation. However, SMILES strings are not inherently unique across sources. The same compound can be represented with different atom ordering, aromaticity notation, stereochemical detail, or source-specific formatting conventions.

This becomes a practical problem before any modeling step begins. If molecular strings are compared exactly as received, equivalent records may fail to match, duplicated compounds may remain in curated tables, and merged datasets may carry representation-level noise into descriptor calculation, fingerprint generation, or machine learning workflows. In some cases, inconsistent molecular strings can also make it harder to identify repeated compounds across training, validation, or external evaluation datasets.

**HARMONSMILE** addresses this preprocessing layer by converting input SMILES into a reproducible RDKit-based representation: canonical, isomeric, and Kekulized. It does not replace chemical curation or RDKit itself; instead, it provides a lightweight and reusable harmonization step for molecular tables, helping researchers prepare more comparable datasets before deduplication, analysis, and machine learning in computational drug discovery.




!!! tip "Core harmonization"
    HARMONSMILE standardizes SMILES to a consistent **canonical + isomeric + Kekulized**
    representation using the RDKit convention widely adopted by the cheminformatics
    community.

## What You Provide and Receive

| You provide | HARMONSMILE returns |
|---|---|
| A tabular molecular dataset from PubChem, ChEMBL, COCONUT, or another source. | Output tables with harmonized SMILES columns added. |
| A SMILES column, or source identifiers for supported PubChem and ChEMBL workflows. | RDKit-based canonical, isomeric, and Kekulized SMILES representations. |
| Optional metadata or identifiers that should be preserved with each record. | Data suitable for comparison, deduplication, curation, and ML preprocessing. |

For installation, examples, command-line usage, pipeline details, and input
formats, see the [Usage](usage.md) page.

## Workflow Overview

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

## Documentation

- [Usage](usage.md) covers installation, quick-start examples, CLI usage, pipelines,
  and input formats.
- [API Reference](api.md) documents public classes, pipelines, and functions.
- [Changelog](changelog.md) lists notable project changes.

## Citation

```text
Contreras-Torres, F. F. (2026). HARMONSMILE: Harmonize SMILES Strings for Cheminformatics and Machine Learning. Zenodo. https://doi.org/10.5281/zenodo.20275498
```

## License

This project is licensed under the terms of the
[GNU Lesser General Public License v3.0 or later](https://github.com/NanoBiostructuresRG/harmonsmile/blob/main/LICENSE).
SPDX identifier: `LGPL-3.0-or-later`.
