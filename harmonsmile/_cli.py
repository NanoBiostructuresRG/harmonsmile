"""
Command-line interface for harmonsmile.

Usage examples:
    harmonsmile --pubchem-in data/db.csv --pubchem-out results/out.csv
    harmonsmile --coconut-in data/db.csv --coconut-smiles SMILES --coconut-out results/out.csv
    python -m harmonsmile --pubchem-in ...
"""

import os
import argparse
from .config import Config
from .pipelines import PubChemIngest, CoconutPrep


def _ensure_dirs():
    for d in ("logs", "results"):
        os.makedirs(d, exist_ok=True)


def _parse(argv=None):
    p = argparse.ArgumentParser(
        prog="harmonsmile",
        description="Harmonize SMILES strings to canonical + isomeric + Kekulized convention.",
    )
    # PubChem
    pub = p.add_argument_group("PubChem")
    pub.add_argument("--pubchem-in",     dest="pub_in",         metavar="FILE")
    pub.add_argument("--pubchem-out",    dest="pub_out",        metavar="FILE")
    pub.add_argument("--pubchem-idcol",  dest="pubchem_idcol",  default="id",          metavar="COL")
    pub.add_argument("--pubchem-cidcol", dest="pubchem_cidcol", default="PubChem CID", metavar="COL")
    # COCONUT / independent
    coco = p.add_argument_group("COCONUT / independent")
    coco.add_argument("--coconut-in",     dest="coco_in",     metavar="FILE")
    coco.add_argument("--coconut-out",    dest="coco_out",    metavar="FILE")
    coco.add_argument("--coconut-smiles", dest="coco_smiles", metavar="COL")
    coco.add_argument("--coconut-idcol",  dest="coconut_idcol", default="id", metavar="COL")
    return p.parse_args(argv)


def main(argv=None):
    _ensure_dirs()
    a = _parse(argv)
    ran_any = False

    if a.pub_in and a.pub_out:
        cfg = Config(
            input_path=a.pub_in,
            output_path=a.pub_out,
            id_col=a.pubchem_idcol,
            cid_col=a.pubchem_cidcol,
        )
        PubChemIngest(cfg).run()
        ran_any = True

    if a.coco_in and a.coco_out and a.coco_smiles:
        CoconutPrep(a.coco_in, a.coco_smiles, a.coco_out).run()
        ran_any = True

    if not ran_any:
        raise SystemExit(
            "Nothing to run. Provide --pubchem-* and/or --coconut-* arguments.\n"
            "Run 'harmonsmile --help' for usage."
        )
