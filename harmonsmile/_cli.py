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

    # Batch modes
    harmonsmile --pubchem-in data/db.csv --pubchem-out results/out.csv
    harmonsmile --chembl-in data/db.csv --chembl-out results/out.csv
    harmonsmile --smiles-in data/db.csv --smiles-col SMILES --smiles-out results/out.csv

    # Single Entry modes
    harmonsmile --pubchem-cid 2723949
    harmonsmile --chembl-id CHEMBL294199

    python -m harmonsmile --pubchem-in data/db.csv --pubchem-out results/out.csv
"""

from __future__ import annotations
from .version import __version__
import argparse
import os
import tempfile
import warnings

import pandas as pd

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

    pub = p.add_argument_group("PubChem (batch)")
    pub.add_argument("--pubchem-in",     dest="pub_in",         metavar="FILE")
    pub.add_argument("--pubchem-out",    dest="pub_out",        metavar="FILE")
    pub.add_argument("--pubchem-cidcol", dest="pubchem_cidcol", default="PubChem CID", metavar="COL")

    chembl = p.add_argument_group("ChEMBL (batch)")
    chembl.add_argument("--chembl-in",    dest="chembl_in",    metavar="FILE")
    chembl.add_argument("--chembl-out",   dest="chembl_out",   metavar="FILE")
    chembl.add_argument("--chembl-idcol", dest="chembl_idcol", default="ChEMBL ID", metavar="COL")

    smiles = p.add_argument_group("SMILES (batch)")
    smiles.add_argument("--smiles-in",  dest="smiles_in",  metavar="FILE")
    smiles.add_argument("--smiles-out", dest="smiles_out", metavar="FILE")
    smiles.add_argument("--smiles-col", dest="smiles_col", metavar="COL")
    # Deprecated --coconut-* aliases — hidden from --help
    smiles.add_argument("--coconut-in",     dest="coconut_in_dep",     metavar="FILE", help=argparse.SUPPRESS)
    smiles.add_argument("--coconut-out",    dest="coconut_out_dep",    metavar="FILE", help=argparse.SUPPRESS)
    smiles.add_argument("--coconut-smiles", dest="coconut_smiles_dep", metavar="COL",  help=argparse.SUPPRESS)

    single = p.add_argument_group("Single Entry")
    single.add_argument("--pubchem-cid", dest="pubchem_cid", metavar="CID")
    single.add_argument("--chembl-id",   dest="chembl_id",   metavar="ID")

    args = p.parse_args(argv)

    # Migrate deprecated --coconut-* values and emit warnings
    _deprecated = [
        ("coconut_in_dep",     "smiles_in",  "--coconut-in",     "--smiles-in"),
        ("coconut_out_dep",    "smiles_out", "--coconut-out",    "--smiles-out"),
        ("coconut_smiles_dep", "smiles_col", "--coconut-smiles", "--smiles-col"),
    ]
    for dep_dest, new_dest, old_flag, new_flag in _deprecated:
        dep_val = getattr(args, dep_dest)
        if dep_val is not None:
            warnings.warn(
                f"{old_flag} is deprecated and will be removed in a future release; "
                f"use {new_flag} instead.",
                DeprecationWarning,
                stacklevel=2,
            )
            if getattr(args, new_dest) is None:
                setattr(args, new_dest, dep_val)

    # Mutual exclusion: single-entry vs batch
    if args.pubchem_cid and args.pub_in:
        p.error("--pubchem-cid and --pubchem-in are mutually exclusive.")
    if args.chembl_id and args.chembl_in:
        p.error("--chembl-id and --chembl-in are mutually exclusive.")

    # Validate paired batch arguments
    if bool(args.pub_in) != bool(args.pub_out):
        p.error("--pubchem-in and --pubchem-out must be provided together.")
    if bool(args.chembl_in) != bool(args.chembl_out):
        p.error("--chembl-in and --chembl-out must be provided together.")
    if bool(args.smiles_in) != bool(args.smiles_out):
        p.error("--smiles-in and --smiles-out must be provided together.")
    if args.smiles_in and not args.smiles_col:
        p.error("--smiles-col is required when --smiles-in is provided.")

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
    Batch mode — PubChem:

    >>> from harmonsmile._cli import main
    >>> main(["--pubchem-in", "data/db.csv", "--pubchem-out", "results/out.csv"])

    Batch mode — ChEMBL:

    >>> main(["--chembl-in", "data/db.csv", "--chembl-out", "results/out.csv"])

    Batch mode — SMILES:

    >>> main(["--smiles-in", "data/db.csv", "--smiles-col", "SMILES",
    ...       "--smiles-out", "results/out.csv"])

    Single Entry — PubChem CID:

    >>> main(["--pubchem-cid", "2723949"])

    Single Entry — ChEMBL ID:

    >>> main(["--chembl-id", "CHEMBL294199"])
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

    if args.smiles_in and args.smiles_out and args.smiles_col:
        _ensure_dirs()
        SMILESPrep(args.smiles_in, args.smiles_col, args.smiles_out).run()
        ran_any = True

    if args.pubchem_cid:
        _ensure_dirs()
        cid = args.pubchem_cid
        out_path = os.path.join("results", f"CID{cid}_harmonsmile.csv")
        tmp = tempfile.NamedTemporaryFile(suffix=".csv", delete=False)
        tmp.close()
        try:
            pd.DataFrame([{"id": 1, "PubChem CID": cid}]).to_csv(tmp.name, index=False)
            cfg = Config(input_path=tmp.name, output_path=out_path)
            PubChemIngest(cfg).run()
        finally:
            os.unlink(tmp.name)
        ran_any = True

    if args.chembl_id:
        _ensure_dirs()
        chembl_id = args.chembl_id
        out_path = os.path.join("results", f"{chembl_id}_harmonsmile.csv")
        tmp = tempfile.NamedTemporaryFile(suffix=".csv", delete=False)
        tmp.close()
        try:
            pd.DataFrame([{"id": 1, "ChEMBL ID": chembl_id}]).to_csv(tmp.name, index=False)
            ChEMBLIngest(
                input_path=tmp.name,
                output_path=out_path,
            ).run()
        finally:
            os.unlink(tmp.name)
        ran_any = True

    if not ran_any:
        raise SystemExit(
            "Nothing to run. Provide --pubchem-*, --chembl-*, --smiles-*, "
            "or single-entry (--pubchem-cid / --chembl-id) arguments.\n"
            "Run 'harmonsmile --help' for usage."
        )
