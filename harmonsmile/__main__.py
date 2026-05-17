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

    python -m harmonsmile --pubchem-in data/db.csv --pubchem-out results/out.csv

Standardize an existing SMILES column::

    python -m harmonsmile --coconut-in data/db.csv --coconut-smiles SMILES --coconut-out results/out.csv
"""

from harmonsmile._cli import main

if __name__ == "__main__":
    main()
