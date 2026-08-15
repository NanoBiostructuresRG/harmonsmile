# SPDX-License-Identifier: LGPL-3.0-or-later
"""
Fetch PubChem compounds by name and save a CSV ready for PubChemIngest.

Usage:
    python fetch_pubchem.py

Output:
    pubchem_fetch_results.csv  — columns: id, PubChem_CID, name
"""

import requests
import pandas as pd

BASE_URL = "https://pubchem.ncbi.nlm.nih.gov/rest/pug"

# --- Configuration ---
QUERY  = "capsaicin"   # Try: "aspirin", "caffeine", "dopamine"
LIMIT  = 20
OUTPUT = "pubchem_fetch_results.csv"


def fetch_cids_by_name(name: str, limit: int = 20) -> list[int]:
    """Fetch PubChem CIDs matching a compound name."""
    url = f"{BASE_URL}/compound/name/{name}/cids/JSON"
    r = requests.get(url, timeout=30, headers={"User-Agent": "harmonsmile (python-requests)"})
    r.raise_for_status()
    cids = r.json().get("IdentifierList", {}).get("CID", [])
    return cids[:limit]


def fetch_name_by_cid(cid: int) -> str | None:
    """Fetch preferred IUPAC name for a CID."""
    url = f"{BASE_URL}/compound/cid/{cid}/property/IUPACName/JSON"
    try:
        r = requests.get(url, timeout=12, headers={"User-Agent": "harmonsmile (python-requests)"})
        r.raise_for_status()
        props = r.json().get("PropertyTable", {}).get("Properties", [{}])
        return props[0].get("IUPACName")
    except Exception:
        return None


def main():
    print(f"Query : {QUERY!r}")
    print(f"Limit : {LIMIT}\n")

    print("Fetching CIDs...")
    cids = fetch_cids_by_name(QUERY, LIMIT)
    print(f"CIDs found: {len(cids)}")

    if not cids:
        print("No results found.")
        return

    rows = []
    for i, cid in enumerate(cids, start=1):
        name = fetch_name_by_cid(cid)
        rows.append({"id": i, "PubChem_CID": str(cid), "name": name})
        print(f"  [{i}/{len(cids)}] CID {cid} — {name}")

    df = pd.DataFrame(rows)
    df.to_csv(OUTPUT, index=False, encoding="utf-8")
    print(f"\nSaved: {OUTPUT}")
    print(df.to_string(index=False))


if __name__ == "__main__":
    main()
