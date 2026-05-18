# SPDX-License-Identifier: LGPL-3.0-or-later
"""
harmonsmile — Harmonize SMILES strings to canonical + isomeric + Kekulized convention.

Provides pipelines and utilities for standardizing SMILES strings using RDKit,
following the COCONUT 2.0 convention: canonical, isomeric, and Kekulized form.

Classes
-------
RDKitStandardizer
    Standardize SMILES strings using RDKit.
Config
    Immutable configuration for harmonsmile pipelines.
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

Harmonize a COCONUT or independent database:

>>> from harmonsmile import CoconutPrep
>>> CoconutPrep(
...     input_path="data/database.csv",
...     smiles_col="SMILES",
...     output_path="results/database_harmonized.csv",
... ).run()

Fetch and harmonize PubChem data:

>>> from harmonsmile import PubChemIngest, Config
>>> cfg = Config(
...     input_path="data/database_pubchem.csv",
...     output_path="results/pubchem_harmonized.csv",
... )
>>> PubChemIngest(cfg).run()
"""

from .standardize import RDKitStandardizer
from .pipelines import PubChemIngest, ChEMBLIngest, SMILESPrep, CoconutPrep
from .config import Config
from .pubchem import PubChemClient
from .io import load_table, save_table
from .version import __version__, PROJECT_NAME, PROJECT_VERSION, PROJECT_STATUS

__author__ = "Flavio F. Contreras-Torres"

__all__ = [
    "RDKitStandardizer",
    "PubChemIngest",
    "ChEMBLIngest",
    "SMILESPrep",
    "Config",
    "load_table",
    "save_table",
    "__version__",
    "PROJECT_NAME",
    "PROJECT_VERSION",
    "PROJECT_STATUS"
]
