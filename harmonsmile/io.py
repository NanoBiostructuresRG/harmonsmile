# SPDX-License-Identifier: LGPL-3.0-or-later
"""
Table I/O utilities for harmonsmile.
"""

from __future__ import annotations
import os
from typing import Any
import pandas as pd


def sanitize_cid(x: Any) -> str | None:
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
    Automatically detects delimiter for text files.

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
        df["PubChem CID"] = df["PubChem CID"].apply(sanitize_cid)
    return df


def save_table(df: pd.DataFrame, path: str | os.PathLike) -> None:
    """
    Save a DataFrame to a CSV file.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame to save.
    path : str or os.PathLike
        Output file path. Parent directories are created if needed.
    """
    os.makedirs(os.path.dirname(os.fspath(path)) or ".", exist_ok=True)
    df.to_csv(path, index=False, encoding="utf-8")
