# SPDX-License-Identifier: LGPL-3.0-or-later
"""
Command-line interface for harmonsmile.

Implements the ``harmonsmile`` entry point and ``python -m harmonsmile``
invocation. Arguments are parsed and forwarded to
:class:`~harmonsmile.pipelines.PubChemIngest`,
:class:`~harmonsmile.pipelines.ChEMBLIngest`, and
:class:`~harmonsmile.pipelines.SMILESPrep`.

Examples
--------
::

    harmonsmile --pubchem-in data/db.csv --pubchem-out results/out.csv
    harmonsmile --chembl-in data/db.csv --chembl-out results/out.csv
    harmonsmile --coconut-in data/db.csv --coconut-smiles SMILES --coconut-out results/out.csv
    python -m harmonsmile --pubchem-in data/db.csv --pubchem-out results/out.csv
"""

from __future__ import annotations
from .version import __version__
import argparse
import os

from .config import Config
from .pipelines import PubChemIngest, ChEMBLIngest, SMILESPrep


def _ensure_dirs() -> None:
    for d in ("logs", "results"):
        os.makedirs(d, exist_ok=True)


def _parse(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="harmonsmile",
        description="Harmonize SMILES strings to canonical + isomeric + Kekulized convention.",
    )
    p.add_argument("--version", action="version", version=f"%(prog)s {__version__}",)
    pub = p.add_argument_group("PubChem")
    pub.add_argument("--pubchem-in",     dest="pub_in",         metavar="FILE")
    pub.add_argument("--pubchem-out",    dest="pub_out",         metavar="FILE")
    pub.add_argument("--pubchem-cidcol", dest="pubchem_cidcol",  default="PubChem CID", metavar="COL")

    chembl = p.add_argument_group("ChEMBL")
    chembl.add_argument("--chembl-in",    dest="chembl_in",    metavar="FILE")
    chembl.add_argument("--chembl-out",   dest="chembl_out",   metavar="FILE")
    chembl.add_argument("--chembl-idcol", dest="chembl_idcol", default="ChEMBL ID", metavar="COL")

    coco = p.add_argument_group("COCONUT / independent")
    coco.add_argument("--coconut-in",     dest="coco_in",     metavar="FILE")
    coco.add_argument("--coconut-out",    dest="coco_out",    metavar="FILE")
    coco.add_argument("--coconut-smiles", dest="coco_smiles", metavar="COL")

    args = p.parse_args(argv)

    # Validate paired arguments
    if bool(args.pub_in) != bool(args.pub_out):
        p.error("--pubchem-in and --pubchem-out must be provided together.")
    if bool(args.chembl_in) != bool(args.chembl_out):
        p.error("--chembl-in and --chembl-out must be provided together.")
    if bool(args.coco_in) != bool(args.coco_out):
        p.error("--coconut-in and --coconut-out must be provided together.")
    if args.coco_in and not args.coco_smiles:
        p.error("--coconut-smiles is required when --coconut-in is provided.")

    return args


def main(argv: list[str] | None = None) -> None:
    """
    Entry point for the harmonsmile command-line interface.

    Parameters
    ----------
    argv : list of str, optional
        Argument list. Defaults to sys.argv if None.

    Examples
    --------
    Programmatic invocation with PubChem pipeline:

    >>> from harmonsmile._cli import main
    >>> main(["--pubchem-in", "data/db.csv", "--pubchem-out", "results/out.csv"])

    Programmatic invocation with ChEMBL pipeline:

    >>> main(["--chembl-in", "data/db.csv", "--chembl-out", "results/out.csv"])

    Programmatic invocation with COCONUT pipeline:

    >>> main(["--coconut-in", "data/db.csv", "--coconut-smiles", "SMILES",
    ...       "--coconut-out", "results/out.csv"])
    """
    args = _parse(argv)
    ran_any = False

    if args.pub_in and args.pub_out:
        _ensure_dirs()
        cfg = Config(
            input_path=args.pub_in,
            output_path=args.pub_out,
            cid_col=args.pubchem_cidcol,
        )
        PubChemIngest(cfg).run()
        ran_any = True

    if args.chembl_in and args.chembl_out:
        _ensure_dirs()
        ChEMBLIngest(
            input_path=args.chembl_in,
            output_path=args.chembl_out,
            chembl_id_col=args.chembl_idcol,
        ).run()
        ran_any = True

    if args.coco_in and args.coco_out and args.coco_smiles:
        _ensure_dirs()
        SMILESPrep(args.coco_in, args.coco_smiles, args.coco_out).run()
        ran_any = True

    if not ran_any:
        raise SystemExit(
            "Nothing to run. Provide --pubchem-*, --chembl-*, and/or --coconut-* arguments.\n"
            "Run 'harmonsmile --help' for usage."
        )
