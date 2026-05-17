# SPDX-License-Identifier: LGPL-3.0-or-later
"""
SMILES standardization utilities based on RDKit.
"""

from rdkit import Chem


class RDKitStandardizer:
    """
    Standardize SMILES strings using RDKit.

    Converts input SMILES to a consistent canonical form following the
    COCONUT 2.0 convention: canonical + isomeric + Kekulized.
    """

    @staticmethod
    def to_iso_kek(smiles: str) -> str | None:
        """
        Convert SMILES to canonical + isomeric + Kekulized form.

        Parameters
        ----------
        smiles : str
            Input SMILES string.

        Returns
        -------
        str or None
            Standardized SMILES, or None if input is invalid.
        """
        if not isinstance(smiles, str) or not smiles.strip():
            return None
        m = Chem.MolFromSmiles(smiles, sanitize=True)
        if m is None:
            return None
        try:
            return Chem.MolToSmiles(m, canonical=True, isomericSmiles=True, kekuleSmiles=True)
        except Exception:
            return None

    @staticmethod
    def to_conn_kek(smiles: str) -> str | None:
        """
        Convert SMILES to canonical + connectivity-only + Kekulized form.

        Stereochemistry is stripped. Useful for connectivity-based comparisons
        where chirality is not relevant.

        Parameters
        ----------
        smiles : str
            Input SMILES string.

        Returns
        -------
        str or None
            Standardized SMILES without stereochemistry, or None if invalid.
        """
        if not isinstance(smiles, str) or not smiles.strip():
            return None
        m = Chem.MolFromSmiles(smiles, sanitize=True)
        if m is None:
            return None
        try:
            return Chem.MolToSmiles(m, canonical=True, isomericSmiles=False, kekuleSmiles=True)
        except Exception:
            return None
