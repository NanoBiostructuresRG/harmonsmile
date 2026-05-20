# SPDX-License-Identifier: LGPL-3.0-or-later
"""
Entry point for running harmonsmile as a module.

Allows the package to be invoked directly from the command line
using ``python -m harmonsmile``. All arguments are forwarded to the
CLI defined in :mod:`harmonsmile._cli`.

See Also
--------
harmonsmile._cli.main : The CLI entry point function.

Examples
--------
Fetch PubChem properties and standardize SMILES::

    python -m harmonsmile --pubchem-in examples/example_pubchem.csv --pubchem-out results/pubchem_out.csv

Fetch ChEMBL properties and standardize SMILES::

    python -m harmonsmile --chembl-in examples/example_chembl.csv --chembl-out results/chembl_out.csv

Standardize an existing SMILES column::

    python -m harmonsmile --smiles-in examples/example_smiles.csv --smiles-col SMILES --smiles-out results/smiles_out.csv

Fetch a single compound by PubChem CID::

    python -m harmonsmile --pubchem-cid 2723949

Fetch a single compound by ChEMBL ID::

    python -m harmonsmile --chembl-id CHEMBL294199
"""

from harmonsmile._cli import main

if __name__ == "__main__":
    main()
