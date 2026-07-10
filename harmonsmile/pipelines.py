# SPDX-License-Identifier: LGPL-3.0-or-later
"""
Harmonization pipelines for PubChem and other databases.

Provides :class:`PubChemIngest` for fetching and standardizing PubChem
compound data, :class:`ChEMBLIngest` for ChEMBL compound data, and
:class:`SMILESPrep` for preparing SMILES from any tabular source.
"""

from __future__ import annotations
import logging
import re

import pandas as pd

from .config import PubChemConfig, ChEMBLConfig, SMILESConfig
from .io import load_table, _drop_accidental_index_columns, _sanitize_cid
from .chembl import _ChEMBLClient
from .pubchem import _PubChemClient
from .standardize import RDKitStandardizer

logger = logging.getLogger(__name__)

PUBCHEM_CID_COLUMN = "PubChem_CID"
_PUBCHEM_CID_ALIAS_KEYS = frozenset({"pubchemcid", "cid"})
_HARMONIZATION_COLUMNS = [
    "SMILES_Harmonized",
    "SMILES_Harmonization_Status",
    "SMILES_Harmonization_Message",
]


def _normalize_pubchem_cid_column_name(column: object) -> str:
    return re.sub(r"[\s_-]+", "", str(column)).casefold()


def _pubchem_alias_columns(df: pd.DataFrame) -> list[str]:
    return [
        col for col in df.columns
        if _normalize_pubchem_cid_column_name(col) in _PUBCHEM_CID_ALIAS_KEYS
    ]


def _resolve_pubchem_cid_column(df: pd.DataFrame, requested: str | None) -> str:
    columns = list(df.columns)
    if requested is not None:
        if requested in df.columns:
            return requested

        requested_key = _normalize_pubchem_cid_column_name(requested)
        matches = [
            col for col in columns
            if _normalize_pubchem_cid_column_name(col) == requested_key
        ]
        if len(matches) == 1:
            return matches[0]
        if len(matches) > 1:
            raise ValueError(
                f"CID column '{requested}' is ambiguous after normalization: {matches}. "
                "Pass --pubchem-cidcol with an explicit unambiguous column."
            )
        raise ValueError(
            f"CID column '{requested}' not found. Available columns: {columns}"
        )

    matches = _pubchem_alias_columns(df)
    if len(matches) == 1:
        return matches[0]
    if len(matches) > 1:
        raise ValueError(
            f"Ambiguous PubChem CID columns found: {matches}. "
            "Pass --pubchem-cidcol with an explicit unambiguous column."
        )
    raise ValueError(
        "No PubChem CID column found. Expected one of "
        "['PubChem_CID', 'PubChem CID', 'PubChemCID', 'CID']. "
        f"Available columns: {columns}"
    )


def _append_harmonization_columns(
    df: pd.DataFrame,
    smiles_col: str,
    std: RDKitStandardizer,
) -> None:
    """
    Append value/status/error columns from lab harmonization.
    """
    results = df[smiles_col].apply(std.to_lab_harmonized)
    df["SMILES_Harmonized"] = results.apply(lambda result: result.value)
    df["SMILES_Harmonization_Status"] = results.apply(lambda result: result.status)
    df["SMILES_Harmonization_Message"] = results.apply(
        lambda result: result.warning or result.error
    )


def _select_output_columns(
    df: pd.DataFrame,
    desired: list[str],
    keep_extra: bool = False,
) -> pd.DataFrame:
    """
    Apply the declared output schema and remove accidental pandas index columns.
    """
    cleaned = _drop_accidental_index_columns(df)
    present = [c for c in desired if c in cleaned.columns]
    if keep_extra:
        extras = [c for c in cleaned.columns if c not in present]
        return cleaned[present + extras]
    return cleaned[present]


class PubChemIngest:
    """
    Pipeline for ingesting and harmonizing PubChem compound data.

    Fetches properties from the PubChem REST API and appends SMILES_RDKit
    plus lab harmonization value/status/error columns. PubChem-provided
    ConnectivitySMILES is preserved when available.

    Parameters
    ----------
    cfg : PubChemConfig
        Pipeline configuration.
    client : _PubChemClient, optional
        PubChem API client. Created automatically if not provided.
    std : RDKitStandardizer, optional
        SMILES standardizer. Created automatically if not provided.

    Examples
    --------
    >>> from harmonsmile import PubChemIngest, PubChemConfig
    >>> cfg = PubChemConfig(
    ...     input_path="examples/example_pubchem.csv",
    ... )
    >>> df = PubChemIngest(cfg).run()
    """

    def __init__(
        self,
        cfg: PubChemConfig,
        client: _PubChemClient | None = None,
        std: RDKitStandardizer | None = None,
    ) -> None:
        self.cfg = cfg
        self.client = client or _PubChemClient(
            logger=lambda m: logger.warning(m)
        )
        self.std = std or RDKitStandardizer()

    def run(self) -> pd.DataFrame:
        """
        Execute the PubChem ingestion pipeline.

        Returns
        -------
        pd.DataFrame
            DataFrame following the PubChem output schema. Extra metadata
            columns are included only when keep_extra_columns=True.

        Raises
        ------
        ValueError
            If the configured CID column is not found in the input file.
        ValueError
            If the input file has zero rows.
        """
        df = load_table(self.cfg.input_path)

        if df.empty:
            raise ValueError(
                f"Input file has zero rows: {self.cfg.input_path}"
            )

        cid_col = _resolve_pubchem_cid_column(df, self.cfg.cid_col)
        if cid_col != PUBCHEM_CID_COLUMN:
            if PUBCHEM_CID_COLUMN in df.columns:
                df = df.drop(columns=[PUBCHEM_CID_COLUMN])
            df = df.rename(columns={cid_col: PUBCHEM_CID_COLUMN})
        df[PUBCHEM_CID_COLUMN] = df[PUBCHEM_CID_COLUMN].apply(_sanitize_cid)

        props = df[PUBCHEM_CID_COLUMN].apply(
            lambda c: self.client.fetch_props(c, list(self.cfg.props))
        )
        props_df = pd.DataFrame(list(props))
        out = pd.concat([df, props_df], axis=1)

        # SMILES_RDKit preserves the v0.2.5 RDKit canonicalization contract.
        if "SMILES" in out.columns:
            out["SMILES_RDKit"] = out["SMILES"].apply(self.std.to_iso_kek)
            _append_harmonization_columns(out, "SMILES", self.std)
        else:
            logger.warning(
                "[PubChemIngest] 'SMILES' column not found after fetching properties "
                "— SMILES_RDKit will not be generated. "
                "Ensure 'SMILES' is included in PubChemConfig.props."
            )

        if "MolecularWeight" in out.columns:
            out.rename(columns={"MolecularWeight": "MW"}, inplace=True)

        desired = [
            "id",
            PUBCHEM_CID_COLUMN,
            "InChI",
            "InChIKey",
            "SMILES",
            "ConnectivitySMILES",
            "SMILES_RDKit",
            *_HARMONIZATION_COLUMNS,
            "MolecularFormula",
            "MW",
            "XLogP",
            "TPSA",
            "Charge",
            "HBondDonorCount",
            "HBondAcceptorCount",
            "RotatableBondCount",
            "HeavyAtomCount",
        ]

        if "MW" in out.columns:
            out["MW"] = pd.to_numeric(out["MW"], errors="coerce")

        out = _select_output_columns(
            out,
            desired,
            keep_extra=self.cfg.keep_extra_columns,
        )

        n     = len(out)
        n_src = out["SMILES"].notna().sum() if "SMILES" in out.columns else 0
        n_rd  = out["SMILES_RDKit"].notna().sum() if "SMILES_RDKit" in out.columns else 0
        logger.info("[OK] PubChemIngest | source SMILES: %s/%s | RDKit: %s/%s", n_src, n, n_rd, n)
        return out


_CHEMBL_RENAME: dict[str, str] = {
    "pref_name":          "name",
    "canonical_smiles":   "SMILES",
    "standard_inchi":     "InChI",
    "standard_inchi_key": "InChIKey",
    "full_mwt":           "MW",
    "full_molformula":    "MolecularFormula",
    "alogp":              "ALogP",
    "psa":                "TPSA",
    "hba":                "HBA",
    "hbd":                "HBD",
    "rtb":                "RotatableBonds",
    "heavy_atoms":        "HeavyAtoms",
    "qed_weighted":       "QED",
    "num_ro5_violations": "Ro5Violations",
}


class ChEMBLIngest:
    """
    Pipeline for ingesting and harmonizing ChEMBL compound data.

    Fetches properties from the ChEMBL REST API by ChEMBL ID and appends
    SMILES_RDKit plus lab harmonization value/status/error columns.

    Parameters
    ----------
    cfg : ChEMBLConfig
        Pipeline configuration.
    client : _ChEMBLClient or None, optional
        ChEMBL API client. Created automatically if not provided.
    std : RDKitStandardizer or None, optional
        SMILES standardizer. Created automatically if not provided.

    Examples
    --------
    >>> from harmonsmile import ChEMBLIngest, ChEMBLConfig
    >>> cfg = ChEMBLConfig(
    ...     input_path="examples/example_chembl.csv",
    ... )
    >>> df = ChEMBLIngest(cfg).run()
    """

    def __init__(
        self,
        cfg: ChEMBLConfig,
        client: _ChEMBLClient | None = None,
        std: RDKitStandardizer | None = None,
    ) -> None:
        self.cfg = cfg
        self.client = client or _ChEMBLClient(
            logger=lambda m: logger.warning(m)
        )
        self.std = std or RDKitStandardizer()

    def run(self) -> pd.DataFrame:
        """
        Execute the ChEMBL ingestion pipeline.

        Returns
        -------
        pd.DataFrame
            DataFrame following the ChEMBL output schema. Extra metadata
            columns are included only when keep_extra_columns=True.

        Raises
        ------
        ValueError
            If the configured ChEMBL ID column is not found in the input file.
        ValueError
            If the input file has zero rows.
        """
        df = load_table(self.cfg.input_path)

        if df.empty:
            raise ValueError(
                f"Input file has zero rows: {self.cfg.input_path}"
            )

        if self.cfg.chembl_id_col not in df.columns:
            raise ValueError(
                f"ChEMBL ID column '{self.cfg.chembl_id_col}' not found. "
                f"Available columns: {list(df.columns)}"
            )

        props = df[self.cfg.chembl_id_col].apply(self.client.fetch_props)
        props_df = pd.DataFrame(list(props))

        # Drop the API's molecule_chembl_id; the input column already holds the ID
        if "molecule_chembl_id" in props_df.columns:
            props_df = props_df.drop(columns=["molecule_chembl_id"])

        out = pd.concat([df, props_df], axis=1)

        # If input already has a 'name' column and the API returned 'pref_name',
        # drop the pre-existing 'name' to avoid duplicate columns after rename.
        if "name" in out.columns and "pref_name" in out.columns:
            out = out.drop(columns=["name"])

        out.rename(columns=_CHEMBL_RENAME, inplace=True)

        # SMILES_RDKit preserves the v0.2.5 RDKit canonicalization contract.
        if "SMILES" in out.columns:
            out["SMILES_RDKit"] = out["SMILES"].apply(self.std.to_iso_kek)
            _append_harmonization_columns(out, "SMILES", self.std)

        desired = [
            "id", "ChEMBL ID", "name", "SMILES", "SMILES_RDKit",
            *_HARMONIZATION_COLUMNS,
            "InChI", "InChIKey", "MW", "MolecularFormula",
            "ALogP", "TPSA", "HBA", "HBD",
            "RotatableBonds", "HeavyAtoms", "QED", "Ro5Violations",
        ]
        _numeric_cols = [
            "MW", "ALogP", "TPSA", "HBA", "HBD",
            "RotatableBonds", "HeavyAtoms", "QED", "Ro5Violations",
        ]
        for col in _numeric_cols:
            if col in out.columns:
                out[col] = pd.to_numeric(out[col], errors="coerce")

        out = _select_output_columns(
            out,
            desired,
            keep_extra=self.cfg.keep_extra_columns,
        )

        n    = len(out)
        n_rd = out["SMILES_RDKit"].notna().sum() if "SMILES_RDKit" in out.columns else 0
        logger.info("[OK] ChEMBLIngest | RDKit: %s/%s", n_rd, n)
        return out


class SMILESPrep:
    """
    Pipeline for preparing SMILES from any tabular source.

    Reads a tabular file and appends SMILES_RDKit plus lab harmonization
    value/status/error columns for the configured source SMILES column.

    Parameters
    ----------
    cfg : SMILESConfig
        Pipeline configuration.
    std : RDKitStandardizer, optional
        SMILES standardizer. Created automatically if not provided.

    Examples
    --------
    >>> from harmonsmile import SMILESPrep, SMILESConfig
    >>> cfg = SMILESConfig(
    ...     input_path="examples/example_smiles.csv",
    ...     smiles_col="SMILES",
    ... )
    >>> df = SMILESPrep(cfg).run()
    """

    def __init__(
        self,
        cfg: SMILESConfig,
        std: RDKitStandardizer | None = None,
    ) -> None:
        self.cfg = cfg
        self.std = std or RDKitStandardizer()

    def run(self) -> pd.DataFrame:
        """
        Execute the SMILES preparation pipeline.

        Returns
        -------
        pd.DataFrame
            DataFrame following the SMILES output schema. Extra metadata
            columns are included only when keep_extra_columns=True.

        Raises
        ------
        ValueError
            If the specified SMILES column is not found in the input file.
        ValueError
            If the input file has zero rows.
        """
        df = load_table(self.cfg.input_path)

        if df.empty:
            raise ValueError(
                f"Input file has zero rows: {self.cfg.input_path}"
            )

        if self.cfg.smiles_col not in df.columns:
            raise ValueError(
                f"Column '{self.cfg.smiles_col}' not found. "
                f"Available columns: {list(df.columns)}"
            )

        df["SMILES_RDKit"] = df[self.cfg.smiles_col].apply(self.std.to_iso_kek)
        _append_harmonization_columns(df, self.cfg.smiles_col, self.std)
        desired = [
            "id",
            self.cfg.smiles_col,
            "SMILES_RDKit",
            *_HARMONIZATION_COLUMNS,
        ]
        out = _select_output_columns(
            df,
            desired,
            keep_extra=self.cfg.keep_extra_columns,
        )

        n, n_ok = len(out), out["SMILES_RDKit"].notna().sum()
        logger.info("[OK] SMILESPrep | RDKit: %s/%s", n_ok, n)
        return out
