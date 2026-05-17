"""
harmonsmile — Harmonize SMILES strings to canonical + isomeric + Kekulized convention.

Quick start:
    from harmonsmile import RDKitStandardizer
    std = RDKitStandardizer()
    std.to_iso_kek("c1ccccc1")   # canonical + isomeric + Kekulized SMILES

    from harmonsmile import CoconutPrep, PubChemIngest, Config
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
