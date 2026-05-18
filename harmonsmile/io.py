# SPDX-License-Identifier: LGPL-3.0-or-later
"""
Table I/O utilities for harmonsmile.

Provides :func:`load_table` and :func:`save_table` for reading and writing
tabular chemical data.
"""

from __future__ import annotations
import os
from typing import Any
import pandas as pd


def _sanitize_cid(x: Any) -> str | None:
    """
    Sanitize a PubChem CID value to a clean numeric string.

    Parameters
    ----------
    x : Any
        Raw CID value (int, float, str, or NaN).

    Returns
    -------
    str or None
        Numeric string CID, or None if the value is missing or invalid.

    Examples
    --------
    >>> _sanitize_cid(2723949.0)
    '2723949'
    >>> _sanitize_cid("  12345  ")
    '12345'
    >>> _sanitize_cid(None)
    """
    if pd.isna(x):
        return None
    try:
        if isinstance(x, float):
            x = int(x)
        s = str(x).strip()
        s = "".join(ch for ch in s if ch.isdigit())
        return s or None
    except Exception:
        return None


def load_table(path: str | os.PathLike) -> pd.DataFrame:
    """
    Load a tabular file into a DataFrame.

    Supports CSV, TSV, TXT, XLSX, XLSM, and XLS formats.
    Automatically detects delimiter for text files; falls back to
    semicolon separator with latin-1 encoding if auto-detection fails.

    Parameters
    ----------
    path : str or os.PathLike
        Path to the input file.

    Returns
    -------
    pd.DataFrame
        Loaded DataFrame with cleaned 'id' and 'PubChem CID' columns
        if present.

    Raises
    ------
    ValueError
        If the file format is not supported.

    Examples
    --------
    >>> df = load_table("data/database_pubchem.csv")
    >>> df = load_table("data/database_coconut.xlsx")
    """
    ext = os.path.splitext(path)[1].lower()
    if ext in (".csv", ".tsv", ".txt"):
        try:
            df = pd.read_csv(path, engine="python", sep=None, encoding="utf-8-sig")
        except Exception:
            df = pd.read_csv(path, sep=";", encoding="latin-1")
    elif ext in (".xlsx", ".xlsm", ".xls"):
        df = pd.read_excel(path)
    else:
        raise ValueError(f"Unsupported format: {path}")

    if "id" in df.columns:
        df["id"] = pd.to_numeric(df["id"], errors="coerce").astype("Int64")
    if "PubChem CID" in df.columns:
        df["PubChem CID"] = df["PubChem CID"].apply(_sanitize_cid)
    return df


def save_table(df: pd.DataFrame, path: str | os.PathLike) -> None:
    """
    Save a DataFrame to a CSV file.

    Parent directories are created automatically if they do not exist.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame to save.
    path : str or os.PathLike
        Output file path.

    Examples
    --------
    >>> import pandas as pd
    >>> df = pd.DataFrame({"SMILES": ["C1=CC=CC=C1"], "SMILES_RDKit": ["C1=CC=CC=C1"]})
    >>> save_table(df, "results/output.csv")
    """
    os.makedirs(os.path.dirname(os.fspath(path)) or ".", exist_ok=True)
    df.to_csv(path, index=False, encoding="utf-8")
