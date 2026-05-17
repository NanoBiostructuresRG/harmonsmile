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
CoconutPrep
    Pipeline for harmonizing SMILES from COCONUT or independent databases.
PubChemClient
    Client for fetching compound properties from the PubChem REST API.

Functions
---------
load_table(path)
    Load a tabular file into a DataFrame.
save_table(df, path)
    Save a DataFrame to a CSV file.

Examples
--------
>>> from harmonsmile import RDKitStandardizer
>>> std = RDKitStandardizer()
>>> std.to_iso_kek("c1ccccc1")
'C1=CC=CC=C1'

>>> from harmonsmile import CoconutPrep, PubChemIngest, Config
"""

from .standardize import RDKitStandardizer
from .pipelines import PubChemIngest, CoconutPrep
from .config import Config
from .pubchem import PubChemClient
from .io import load_table, save_table

__version__ = "0.1.0"
__author__ = "Flavio F. Contreras-Torres"

__all__ = [
    "RDKitStandardizer",
    "PubChemIngest",
    "CoconutPrep",
    "Config",
    "PubChemClient",
    "load_table",
    "save_table",
    "__version__",
]
