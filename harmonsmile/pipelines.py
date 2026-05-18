# SPDX-License-Identifier: LGPL-3.0-or-later
"""
Harmonization pipelines for PubChem and COCONUT databases.

Provides :class:`PubChemIngest` for fetching and standardizing PubChem
compound data, and :class:`CoconutPrep` for harmonizing SMILES from
COCONUT or independent molecular databases.
"""

from __future__ import annotations
import logging
import os

import pandas as pd

from .config import Config
from .io import load_table, save_table
from .pubchem import PubChemClient
from .standardize import RDKitStandardizer

logger = logging.getLogger(__name__)


class PubChemIngest:
    """
    Pipeline for ingesting and harmonizing PubChem compound data.

    Fetches properties from the PubChem REST API and appends a
    standardized SMILES_RDKit column using RDKit canonicalization.

    Parameters
    ----------
    cfg : Config
        Pipeline configuration.
    client : PubChemClient, optional
        PubChem API client. Created automatically if not provided.
    std : RDKitStandardizer, optional
        SMILES standardizer. Created automatically if not provided.

    Examples
    --------
    >>> from harmonsmile import PubChemIngest, Config
    >>> cfg = Config(
    ...     input_path="data/database_pubchem.csv",
    ...     output_path="results/pubchem_harmonized.csv",
    ... )
    >>> df = PubChemIngest(cfg).run()
    """

    def __init__(
        self,
        cfg: Config,
        client: PubChemClient | None = None,
        std: RDKitStandardizer | None = None,
    ) -> None:
        self.cfg = cfg
        self.client = client or PubChemClient(
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
        """
        df = load_table(self.cfg.input_path)

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

        if "MolecularWeight" in out.columns:
            out.rename(columns={"MolecularWeight": "MW"}, inplace=True)

        desired = ["id", "PubChem CID", "MW", "SMILES", "SMILES_RDKit"]
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


class SMILESPrep:
    """
    Pipeline for harmonizing SMILES from COCONUT or independent databases.

    Reads a tabular file, applies RDKit canonicalization to the specified
    SMILES column, and saves the result with an appended SMILES_RDKit column.

    Parameters
    ----------
    input_path : str or os.PathLike
        Path to the input file.
    smiles_col : str
        Name of the column containing SMILES strings.
    output_path : str or os.PathLike
        Path to the output CSV file.
    std : RDKitStandardizer, optional
        SMILES standardizer. Created automatically if not provided.

    Examples
    --------
    >>> from harmonsmile import CoconutPrep
    >>> df = CoconutPrep(
    ...     input_path="data/database_coconut.csv",
    ...     smiles_col="SMILES",
    ...     output_path="results/coconut_harmonized.csv",
    ... ).run()
    """

    def __init__(
        self,
        input_path: str | os.PathLike,
        smiles_col: str,
        output_path: str | os.PathLike,
        std: RDKitStandardizer | None = None,
    ) -> None:
        self.input_path  = input_path
        self.smiles_col  = smiles_col
        self.output_path = output_path
        self.std         = std or RDKitStandardizer()

    def run(self) -> pd.DataFrame:
        """
        Execute the COCONUT preparation pipeline.

        Returns
        -------
        pd.DataFrame
            DataFrame with original columns plus standardized SMILES_RDKit column.

        Raises
        ------
        ValueError
            If the specified SMILES column is not found in the input file.
        """
        os.makedirs(os.path.dirname(os.fspath(self.output_path)) or ".", exist_ok=True)
        df = load_table(self.input_path)
        if self.smiles_col not in df.columns:
            raise ValueError(
                f"Column '{self.smiles_col}' not found. "
                f"Available columns: {list(df.columns)}"
            )
        df["SMILES_RDKit"] = df[self.smiles_col].apply(self.std.to_iso_kek)
        save_table(df, self.output_path)
        n, n_ok = len(df), df["SMILES_RDKit"].notna().sum()
        logger.info("[OK] %s | RDKit: %s/%s", self.output_path, n_ok, n)
        return df


# Deprecated alias — will be removed in a future release
CoconutPrep = SMILESPrep
