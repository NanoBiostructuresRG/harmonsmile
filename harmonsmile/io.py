# SPDX-License-Identifier: LGPL-3.0-or-later
"""
Table I/O utilities for harmonsmile.

Provides :func:`load_table` and :func:`save_table` for reading and writing
tabular chemical data.
"""

from __future__ import annotations

import os
import re
from typing import Any

import pandas as pd

_UNNAMED_INDEX_RE = re.compile(
    r"^unnamed(?:[:_\s.-]*\d+)+(?:[:_\s.-]*level[:_\s.-]*\d+)?$",
    re.IGNORECASE,
)


def _is_accidental_index_column(column: Any) -> bool:
    """Return True for pandas-generated index columns such as Unnamed: 0."""
    return bool(_UNNAMED_INDEX_RE.match(str(column).strip()))


def _drop_accidental_index_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Remove pandas-generated index columns without mutating the input frame."""
    drop_cols = [c for c in df.columns if _is_accidental_index_column(c)]
    if not drop_cols:
        return df
    return df.drop(columns=drop_cols)


def _validate_output_path(path: str | os.PathLike) -> None:
    """Validate the package write boundary path."""
    output = os.fspath(path)
    if not output:
        raise ValueError("output path must not be empty.")
    parts = re.split(r"[\\/]+", output)
    if ".." in parts:
        raise ValueError("output path must not contain path traversal patterns ('..').")


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
    >>> _sanitize_cid(True)
    >>> _sanitize_cid([1, 2, 3])
    """
    try:
        if pd.isna(x):
            return None
    except (TypeError, ValueError):
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

    Supports CSV, TSV, TXT, XLSX, XLSM, and XLS formats. CSV files use
    comma delimiters, TSV/TXT files use tab delimiters, and Excel files
    are loaded with :func:`pandas.read_excel`.

    Parameters
    ----------
    path : str or os.PathLike
        Path to the input file.

    Returns
    -------
    pd.DataFrame
        Loaded DataFrame with cleaned 'id' column if present.

    Raises
    ------
    FileNotFoundError
        If the file does not exist at the given path.
    ValueError
        If the file format is not supported.
    ValueError
        If the loaded DataFrame has zero rows.

    Examples
    --------
    >>> df = load_table("examples/example_chembl.csv")
    >>> df = load_table("examples/example_pubchem.csv")
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"Input file not found: {path}")

    ext = os.path.splitext(path)[1].lower()
    if ext == ".csv":
        df = pd.read_csv(path, sep=",", encoding="utf-8-sig")
    elif ext in (".tsv", ".txt"):
        df = pd.read_csv(path, sep="\t", encoding="utf-8-sig")
    elif ext in (".xlsx", ".xlsm", ".xls"):
        df = pd.read_excel(path)
    else:
        raise ValueError(f"Unsupported format: {path}")

    df = _drop_accidental_index_columns(df)

    if df.empty:
        raise ValueError(f"Input file has zero rows: {path}")

    if "id" in df.columns:
        df["id"] = pd.to_numeric(df["id"], errors="coerce").astype("Int64")
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
        Output file path. Parent directories are created as needed.

    Examples
    --------
    >>> import pandas as pd
    >>> df = pd.DataFrame({"SMILES": ["C1=CC=CC=C1"], "SMILES_RDKit": ["C1=CC=CC=C1"]})
    >>> save_table(df, "results/output.csv")
    """
    _validate_output_path(path)
    os.makedirs(os.path.dirname(os.fspath(path)) or ".", exist_ok=True)
    df.to_csv(path, index=False, encoding="utf-8")
