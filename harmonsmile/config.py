# SPDX-License-Identifier: LGPL-3.0-or-later
"""
Configuration dataclass for harmonsmile pipelines.

Defines the immutable :class:`Config` object used by
:class:`~harmonsmile.pipelines.PubChemIngest` to parameterize
input/output paths, PubChem column names, and properties to fetch.
"""

from __future__ import annotations
from dataclasses import dataclass

VALID_PUBCHEM_PROPS: frozenset[str] = frozenset({
    "SMILES", "ConnectivitySMILES", "MolecularWeight",
    "MolecularFormula", "InChI", "InChIKey", "XLogP", "TPSA",
    "HBondDonorCount", "HBondAcceptorCount", "RotatableBondCount",
    "HeavyAtomCount", "Charge",
})


@dataclass(frozen=True)
class Config:
    """
    Immutable configuration for harmonsmile pipelines.

    Parameters
    ----------
    input_path : str
        Path to the input file (CSV, TSV, XLSX).
    output_path : str
        Path to the output CSV file.
    error_log : str, optional
        Path to the error log file. Defaults to 'logs/errors.txt'.
    cid_col : str, optional
        Name of the PubChem CID column. Defaults to 'PubChem CID'.
    props : tuple of str, optional
        PubChem properties to fetch. Defaults to ('SMILES', 'MolecularWeight').
    """

    input_path: str
    output_path: str
    error_log: str = "logs/errors.txt"
    cid_col: str = "PubChem CID"
    props: tuple[str, ...] = ("SMILES", "MolecularWeight")

    def __post_init__(self) -> None:
        if not self.input_path:
            raise ValueError("input_path must not be empty.")
        if not self.output_path:
            raise ValueError("output_path must not be empty.")
        if ".." in self.output_path:
            raise ValueError("output_path must not contain path traversal patterns ('..').")
        if not self.props:
            raise ValueError("props must contain at least one PubChem property.")
        invalid = {p for p in self.props if p not in VALID_PUBCHEM_PROPS}
        if invalid:
            raise ValueError(f"Invalid PubChem properties: {sorted(invalid)}")
