# SPDX-License-Identifier: LGPL-3.0-or-later
"""
SMILES standardization utilities based on RDKit.

Provides :class:`RDKitStandardizer` for converting SMILES strings to
canonical + isomeric + Kekulized form, following the COCONUT 2.0 convention.
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
        
        Notes
        -----
        Chiral centers (e.g. ``[C@@H]``) are preserved because RDKit encodes
        tetrahedral stereochemistry independently of kekulization.

        E/Z geometry on double bonds (``/`` and ``\`` in SMILES) is preserved
        only when RDKit can unambiguously determine the configuration after
        parsing and sanitization. For some double bonds — particularly those
        in conjugated systems or where the source SMILES omits directional
        bonds on one side — RDKit cannot resolve the geometry and silently
        drops the ``/``/``\`` notation. This is a known RDKit behavior, not a
        bug in harmonsmile. If E/Z fidelity is critical for your use case,
        validate ``SMILES_RDKit`` against the source SMILES.

        Examples
        --------
        >>> RDKitStandardizer.to_iso_kek("c1ccccc1")
        'C1=CC=CC=C1'
        >>> RDKitStandardizer.to_iso_kek("invalid")
        >>> RDKitStandardizer.to_iso_kek("")
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

        Examples
        --------
        >>> RDKitStandardizer.to_conn_kek("C[C@@H](O)F")
        'CC(O)F'
        >>> RDKitStandardizer.to_conn_kek("invalid")
        >>> RDKitStandardizer.to_conn_kek("")
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
