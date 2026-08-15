# SPDX-License-Identifier: LGPL-3.0-or-later
"""
Configuration dataclasses for harmonsmile pipelines.

Defines immutable configuration objects for each pipeline:
:class:`PubChemConfig` for :class:`~harmonsmile.pipelines.PubChemIngest`,
:class:`ChEMBLConfig` for :class:`~harmonsmile.pipelines.ChEMBLIngest`, and
:class:`SMILESConfig` for :class:`~harmonsmile.pipelines.SMILESPrep`.
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
class PubChemConfig:
    """
    Immutable configuration for :class:`~harmonsmile.pipelines.PubChemIngest`.

    Parameters
    ----------
    input_path : str
        Path to the input file (CSV, TSV, XLSX). Must not be empty or
        contain path traversal patterns ('..').
    cid_col : str, optional
        Name of the PubChem CID column. Must not be empty or
        whitespace-only when provided. Defaults to None, which enables
        deterministic alias-based auto-detection.
    props : tuple of str, optional
        PubChem properties to fetch. Must contain at least one valid
        property name. Defaults to all available properties.
    keep_extra_columns : bool, optional
        Preserve input metadata columns outside the declared output schema.
        Defaults to False.

    Raises
    ------
    ValueError
        If ``input_path`` is empty or contains '..'.
    ValueError
        If ``cid_col`` is empty or whitespace-only.
    ValueError
        If ``props`` is empty or contains invalid property names.

    Examples
    --------
    >>> from harmonsmile import PubChemConfig
    >>> cfg = PubChemConfig(
    ...     input_path="examples/example_pubchem.csv",
    ... )
    """

    input_path: str
    cid_col: str | None = None
    props: tuple[str, ...] = (
        "SMILES", "ConnectivitySMILES", "MolecularFormula",
        "MolecularWeight", "InChI", "InChIKey", "XLogP", "TPSA",
        "Charge", "HBondDonorCount", "HBondAcceptorCount",
        "RotatableBondCount", "HeavyAtomCount",
    )
    keep_extra_columns: bool = False

    def __post_init__(self) -> None:
        if not self.input_path:
            raise ValueError("input_path must not be empty.")
        if ".." in self.input_path:
            raise ValueError("input_path must not contain path traversal patterns ('..').")
        if self.cid_col is not None and not self.cid_col.strip():
            raise ValueError("cid_col must not be empty.")
        if not self.props:
            raise ValueError("props must contain at least one PubChem property.")
        invalid = {p for p in self.props if p not in VALID_PUBCHEM_PROPS}
        if invalid:
            raise ValueError(f"Invalid PubChem properties: {sorted(invalid)}")
        if not isinstance(self.keep_extra_columns, bool):
            raise ValueError("keep_extra_columns must be a bool.")


@dataclass(frozen=True)
class ChEMBLConfig:
    """
    Immutable configuration for :class:`~harmonsmile.pipelines.ChEMBLIngest`.

    Parameters
    ----------
    input_path : str
        Path to the input file (CSV, TSV, XLSX). Must not be empty or
        contain path traversal patterns ('..').
    chembl_id_col : str, optional
        Name of the ChEMBL ID column in the input file. Must not be
        empty or whitespace-only. Defaults to 'ChEMBL ID'.
    keep_extra_columns : bool, optional
        Preserve input metadata columns outside the declared output schema.
        Defaults to False.

    Raises
    ------
    ValueError
        If ``input_path`` is empty or contains '..'.
    ValueError
        If ``chembl_id_col`` is empty or whitespace-only.

    Examples
    --------
    >>> from harmonsmile import ChEMBLConfig
    >>> cfg = ChEMBLConfig(
    ...     input_path="examples/example_chembl.csv",
    ... )
    """

    input_path: str
    chembl_id_col: str = "ChEMBL ID"
    keep_extra_columns: bool = False

    def __post_init__(self) -> None:
        if not self.input_path:
            raise ValueError("input_path must not be empty.")
        if ".." in self.input_path:
            raise ValueError("input_path must not contain path traversal patterns ('..').")
        if not self.chembl_id_col or not self.chembl_id_col.strip():
            raise ValueError("chembl_id_col must not be empty.")
        if not isinstance(self.keep_extra_columns, bool):
            raise ValueError("keep_extra_columns must be a bool.")


@dataclass(frozen=True)
class SMILESConfig:
    """
    Immutable configuration for :class:`~harmonsmile.pipelines.SMILESPrep`.

    Parameters
    ----------
    input_path : str
        Path to the input file (CSV, TSV, XLSX). Must not be empty or
        contain path traversal patterns ('..').
    smiles_col : str
        Name of the column containing SMILES strings. Must not be
        empty or whitespace-only.
    keep_extra_columns : bool, optional
        Preserve input metadata columns outside the declared output schema.
        Defaults to False.

    Raises
    ------
    ValueError
        If ``input_path`` is empty or contains '..'.
    ValueError
        If ``smiles_col`` is empty or whitespace-only.

    Examples
    --------
    >>> from harmonsmile import SMILESConfig
    >>> cfg = SMILESConfig(
    ...     input_path="examples/example_smiles.csv",
    ...     smiles_col="SMILES",
    ... )
    """

    input_path: str
    smiles_col: str
    keep_extra_columns: bool = False

    def __post_init__(self) -> None:
        if not self.input_path:
            raise ValueError("input_path must not be empty.")
        if ".." in self.input_path:
            raise ValueError("input_path must not contain path traversal patterns ('..').")
        if not self.smiles_col or not self.smiles_col.strip():
            raise ValueError("smiles_col must not be empty.")
        if not isinstance(self.keep_extra_columns, bool):
            raise ValueError("keep_extra_columns must be a bool.")
