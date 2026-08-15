# SPDX-License-Identifier: LGPL-3.0-or-later
"""
harmonsmile — Harmonize SMILES strings to canonical + isomeric + Kekulized convention.

Provides pipelines and utilities for standardizing SMILES strings using RDKit,
following the COCONUT 2.0 convention: canonical, isomeric, and Kekulized form.

Classes
-------
RDKitStandardizer
    Standardize SMILES strings using RDKit.
HarmonizationResult
    Typed result returned by lab harmonization.
PubChemConfig
    Immutable configuration for PubChemIngest.
ChEMBLConfig
    Immutable configuration for ChEMBLIngest.
SMILESConfig
    Immutable configuration for SMILESPrep.
PubChemIngest
    Pipeline for ingesting and harmonizing PubChem compound data.
ChEMBLIngest
    Pipeline for ingesting and harmonizing ChEMBL compound data.
SMILESPrep
    Pipeline for harmonizing SMILES from any tabular source.

Functions
---------
load_table(path)
    Load a tabular file into a DataFrame.
save_table(df, path)
    Save a DataFrame to a CSV file.

Examples
--------
Standardize a single SMILES string:

>>> from harmonsmile import RDKitStandardizer
>>> std = RDKitStandardizer()
>>> std.to_iso_kek("c1ccccc1")
'C1=CC=CC=C1'
>>> std.to_conn_kek("C[C@@H](O)F")
'CC(O)F'

Harmonize any file with a SMILES column:

>>> from harmonsmile import SMILESPrep, SMILESConfig, save_table
>>> cfg = SMILESConfig(
...     input_path="examples/example_smiles.csv",
...     smiles_col="SMILES",
... )
>>> df = SMILESPrep(cfg).run()
>>> save_table(df, "results/smiles_harmonized.csv")

Fetch and harmonize PubChem data:

>>> from harmonsmile import PubChemIngest, PubChemConfig, save_table
>>> cfg = PubChemConfig(
...     input_path="examples/example_pubchem.csv",
... )
>>> df = PubChemIngest(cfg).run()
>>> save_table(df, "results/pubchem_harmonized.csv")

Fetch and harmonize ChEMBL data:

>>> from harmonsmile import ChEMBLIngest, ChEMBLConfig, save_table
>>> cfg = ChEMBLConfig(
...     input_path="examples/example_chembl.csv",
... )
>>> df = ChEMBLIngest(cfg).run()
>>> save_table(df, "results/chembl_harmonized.csv")
"""

from .config import ChEMBLConfig, PubChemConfig, SMILESConfig
from .io import load_table, save_table
from .pipelines import ChEMBLIngest, PubChemIngest, SMILESPrep
from .standardize import HarmonizationResult, RDKitStandardizer
from .version import PROJECT_NAME, PROJECT_STATUS, PROJECT_VERSION, __version__

__author__ = "Flavio F. Contreras-Torres"

__all__ = [
    "PROJECT_NAME",
    "PROJECT_STATUS",
    "PROJECT_VERSION",
    "ChEMBLConfig",
    "ChEMBLIngest",
    "HarmonizationResult",
    "PubChemConfig",
    "PubChemIngest",
    "RDKitStandardizer",
    "SMILESConfig",
    "SMILESPrep",
    "__version__",
    "load_table",
    "save_table",
]
