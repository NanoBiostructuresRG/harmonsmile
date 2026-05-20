# SPDX-License-Identifier: LGPL-3.0-or-later
"""
Harmonization pipelines for PubChem and other databases.

Provides :class:`PubChemIngest` for fetching and standardizing PubChem
compound data, :class:`ChEMBLIngest` for ChEMBL compound data, and
:class:`SMILESPrep` for harmonizing SMILES from any tabular source.
"""

from __future__ import annotations
import logging
import os

import pandas as pd

from .config import PubChemConfig, ChEMBLConfig, SMILESConfig
from .io import load_table, save_table
from .chembl import _ChEMBLClient
from .pubchem import _PubChemClient
from .standardize import RDKitStandardizer

logger = logging.getLogger(__name__)


class PubChemIngest:
    """
    Pipeline for ingesting and harmonizing PubChem compound data.

    Fetches properties from the PubChem REST API and appends a
    standardized SMILES_RDKit column using RDKit canonicalization.

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
    ...     output_path="results/pubchem_harmonized.csv",
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
            DataFrame with original columns plus fetched properties
            and standardized SMILES_RDKit column.

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

        if self.cfg.cid_col not in df.columns:
            raise ValueError(
                f"CID column '{self.cfg.cid_col}' not found. "
                f"Available columns: {list(df.columns)}"
            )

        props = df[self.cfg.cid_col].apply(
            lambda c: self.client.fetch_props(c, list(self.cfg.props))
        )
        props_df = pd.DataFrame(list(props))
        out = pd.concat([df, props_df], axis=1)

        # SMILES harmonization to COCONUT 2.0 convention
        if "SMILES" in out.columns:
            out["SMILES_RDKit"] = out["SMILES"].apply(self.std.to_iso_kek)
        else:
            logger.warning(
                "[PubChemIngest] 'SMILES' column not found after fetching properties "
                "— SMILES_RDKit will not be generated. "
                "Ensure 'SMILES' is included in PubChemConfig.props."
            )

        if "MolecularWeight" in out.columns:
            out.rename(columns={"MolecularWeight": "MW"}, inplace=True)

        desired = ["id", "PubChem CID",
                   "SMILES", "SMILES_RDKit", "ConnectivitySMILES",
                   "MolecularFormula", "MW", "InChI", "InChIKey",
                   "XLogP", "TPSA", "Charge",
                   "HBondDonorCount", "HBondAcceptorCount",
                   "RotatableBondCount", "HeavyAtomCount",
                   ]

        present = [c for c in desired if c in out.columns]
        others  = [c for c in out.columns if c not in present]

        if "MW" in out.columns:
            out["MW"] = pd.to_numeric(out["MW"], errors="coerce")

        out = out[present + others]
        save_table(out, self.cfg.output_path)

        n     = len(out)
        n_src = out["SMILES"].notna().sum() if "SMILES" in out.columns else 0
        n_rd  = out["SMILES_RDKit"].notna().sum() if "SMILES_RDKit" in out.columns else 0
        logger.info("[OK] %s | source SMILES: %s/%s | RDKit: %s/%s", self.cfg.output_path, n_src, n, n_rd, n)
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

    Fetches properties from the ChEMBL REST API by ChEMBL ID, applies
    RDKit canonicalization to produce a standardized SMILES_RDKit column,
    and saves the result as a CSV file.

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
    ...     output_path="results/chembl_harmonized.csv",
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
            DataFrame with original columns plus fetched and renamed
            ChEMBL properties and a standardized SMILES_RDKit column.

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

        # SMILES harmonization to COCONUT 2.0 convention
        if "SMILES" in out.columns:
            out["SMILES_RDKit"] = out["SMILES"].apply(self.std.to_iso_kek)

        desired = [
            "id", "ChEMBL ID", "name", "SMILES", "SMILES_RDKit",
            "InChI", "InChIKey", "MW", "MolecularFormula",
            "ALogP", "TPSA", "HBA", "HBD",
            "RotatableBonds", "HeavyAtoms", "QED", "Ro5Violations",
        ]
        present = [c for c in desired if c in out.columns]
        others  = [c for c in out.columns if c not in present]

        _numeric_cols = [
            "MW", "ALogP", "TPSA", "HBA", "HBD",
            "RotatableBonds", "HeavyAtoms", "QED", "Ro5Violations",
        ]
        for col in _numeric_cols:
            if col in out.columns:
                out[col] = pd.to_numeric(out[col], errors="coerce")

        out = out[present + others]
        save_table(out, self.cfg.output_path)

        n    = len(out)
        n_rd = out["SMILES_RDKit"].notna().sum() if "SMILES_RDKit" in out.columns else 0
        logger.info("[OK] %s | RDKit: %s/%s", self.cfg.output_path, n_rd, n)
        return out


class SMILESPrep:
    """
    Pipeline for harmonizing SMILES from any tabular source.

    Reads a tabular file, applies RDKit canonicalization to the specified
    SMILES column, and saves the result with an appended SMILES_RDKit column.

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
    ...     output_path="results/smiles_harmonized.csv",
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
            DataFrame with original columns plus standardized SMILES_RDKit column.

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
        save_table(df, self.cfg.output_path)

        n, n_ok = len(df), df["SMILES_RDKit"].notna().sum()
        logger.info("[OK] %s | RDKit: %s/%s", self.cfg.output_path, n_ok, n)
        return df
