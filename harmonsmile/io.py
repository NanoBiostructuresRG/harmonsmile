import os
import pandas as pd


def sanitize_cid(x) -> str | None:
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


def load_table(path: str) -> pd.DataFrame:
    ext = os.path.splitext(path)[1].lower()
    if ext in (".csv", ".tsv", ".txt"):
        try:
            df = pd.read_csv(path, engine="python", sep=None, encoding="utf-8-sig")
        except Exception:
            df = pd.read_csv(path, sep=";", encoding="utf-8-sig")
    elif ext in (".xlsx", ".xlsm", ".xls"):
        df = pd.read_excel(path)
    else:
        raise ValueError(f"Unsupported format: {path}")

    if "id" in df.columns:
        df["id"] = pd.to_numeric(df["id"], errors="coerce").astype("Int64")
    if "PubChem CID" in df.columns:
        df["PubChem CID"] = df["PubChem CID"].apply(sanitize_cid)
    return df


def save_table(df: pd.DataFrame, path: str) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    df.to_csv(path, index=False, encoding="utf-8")
