# Recommended use (single entry point):
#   python -m harmonsmile --pubchem-in data\database_pubchem.csv --pubchem-out results\pubchem_harmonized.csv
#   python -m harmonsmile --coconut-in data\database_coconut.csv --coconut-smiles SMILES --coconut-out results\coconut_harmonized.csv
#   python -m harmonsmile first part ^ second part
#
# Alternative (equivalent):
#   python -m cli.harmonize ...  # same flags

import os
import argparse
from harmonsmile.config import Config
from harmonsmile.pipelines import PubChemIngest, CoconutPrep

def ensure_dirs():
    for d in ("logs", "results"):
        os.makedirs(d, exist_ok=True)
        
def parse():
    p = argparse.ArgumentParser(description="Harmonize SMILES (PubChem and/or COCONUT) in a single run.")
    # PubChem
    p.add_argument("--pubchem-in",  dest="pub_in")
    p.add_argument("--pubchem-out", dest="pub_out")
    p.add_argument("--pubchem-idcol",  default="id")
    p.add_argument("--pubchem-cidcol", default="PubChem CID")
    # COCONUT
    p.add_argument("--coconut-in",   dest="coco_in")
    p.add_argument("--coconut-out",  dest="coco_out")
    p.add_argument("--coconut-idcol",  default="id")
    p.add_argument("--coconut-smiles", dest="coco_smiles")
    return p.parse_args()

def main():
    ensure_dirs()
    a = parse()
    ran_any = False

    # PubChem (optional)
    if a.pub_in and a.pub_out:
        cfg = Config(input_path=a.pub_in, output_path=a.pub_out,
                     id_col=a.pubchem_idcol, cid_col=a.pubchem_cidcol)
        PubChemIngest(cfg).run()
        ran_any = True

    # COCONUT (optional)
    if a.coco_in and a.coco_out and a.coco_smiles:
        CoconutPrep(a.coco_in, a.coco_smiles, a.coco_out).run()
        ran_any = True

    if not ran_any:
        raise SystemExit("Nothing to run. Provides --pubchem-* and/or --coconut-* as appropiate.")

if __name__ == "__main__":
    main()
