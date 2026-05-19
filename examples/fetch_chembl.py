# SPDX-License-Identifier: LGPL-3.0-or-later
"""
Fetch ChEMBL compounds by free-text query and save a CSV ready for ChEMBLIngest.

Usage:
    python fetch_chembl.py

Output:
    chembl_fetch_results.csv  — columns: id, ChEMBL ID, name, molecule_type, max_phase
"""

import requests
import pandas as pd
from urllib.parse import urlencode

BASE_URL = "https://www.ebi.ac.uk/chembl/api/data"

# --- Configuration ---
QUERY  = "capsaicin"   # Try: "kinase inhibitor", "PPAR", "dopamine receptor"
LIMIT  = 20
OFFSET = 0
OUTPUT = "chembl_fetch_results.csv"


def chembl_get_json(endpoint: str, params: dict | None = None, timeout: int = 30) -> dict:
    """Fetch JSON from ChEMBL REST API."""
    endpoint = endpoint.lstrip("/")
    url = f"{BASE_URL}/{endpoint}"
    headers = {"Accept": "application/json"}
    r = requests.get(url, params=params, headers=headers, timeout=timeout)
    r.raise_for_status()
    return r.json()


def main():
    params = {"q": QUERY, "limit": LIMIT, "offset": OFFSET}
    url = f"{BASE_URL}/molecule/search?{urlencode(params)}"
    print(f"Query : {QUERY!r}")
    print(f"URL   : {url}\n")

    data = chembl_get_json("molecule/search", params=params)
    rows = data.get("molecules", [])
    print(f"Results returned: {len(rows)}")

    if not rows:
        print("No results found.")
        return

    df = pd.json_normalize(rows)

    # Build output DataFrame ready for ChEMBLIngest
    out = pd.DataFrame()
    out["id"]            = range(1, len(df) + 1)
    out["ChEMBL ID"]     = df.get("molecule_chembl_id", pd.Series())
    out["name"]          = df.get("pref_name", pd.Series())
    out["molecule_type"] = df.get("molecule_type", pd.Series())
    out["max_phase"]     = df.get("max_phase", pd.Series())

    out.to_csv(OUTPUT, index=False, encoding="utf-8")
    print(f"\nSaved: {OUTPUT}")
    print(out[["id", "ChEMBL ID", "name", "max_phase"]].to_string(index=False))


if __name__ == "__main__":
    main()
