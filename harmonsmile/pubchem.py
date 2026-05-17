# SPDX-License-Identifier: LGPL-3.0-or-later
"""
PubChem REST API client for harmonsmile.

Provides :class:`PubChemClient` for fetching compound properties from the
PubChem REST API, with exponential backoff and persistent connection reuse.
"""

from __future__ import annotations
import logging
import time
from typing import Any, Callable

import requests


class PubChemClient:
    """
    Client for fetching compound properties from the PubChem REST API.

    Uses exponential backoff on failure and a persistent requests.Session
    for efficient connection reuse across multiple compounds.

    Parameters
    ----------
    logger : Callable[[str], None] or None, optional
        Callable for error reporting. Defaults to the module logger warning.
    sleep : float, optional
        Base sleep time in seconds between requests. Defaults to 0.2.
    retries : int, optional
        Number of retry attempts on failure. Defaults to 3.

    Examples
    --------
    >>> client = PubChemClient()
    >>> props = client.fetch_props("2723949", ["SMILES", "MolecularWeight"])
    >>> client.close()
    """

    def __init__(
        self,
        logger: Callable[[str], None] | None = None,
        sleep: float = 0.2,
        retries: int = 3,
    ) -> None:
        self.log = logger or (lambda m: logging.getLogger(__name__).warning(m))
        self.sleep = sleep
        self.retries = retries
        self._session = requests.Session()
        self._session.headers.update({"User-Agent": "harmonsmile (python-requests)"})

    def fetch_props(self, cid: str, props: list[str]) -> dict[str, Any]:
        """
        Fetch compound properties from PubChem by CID.

        Parameters
        ----------
        cid : str
            PubChem Compound ID.
        props : list of str
            List of property names to fetch (e.g. ['SMILES', 'MolecularWeight']).

        Returns
        -------
        dict[str, Any]
            Dictionary mapping property names to their values.
            Values are None if the fetch failed or CID is empty.

        Examples
        --------
        >>> client = PubChemClient()
        >>> client.fetch_props("2723949", ["SMILES", "MolecularWeight"])
        {'SMILES': '...', 'MolecularWeight': ...}
        >>> client.fetch_props("", ["SMILES"])
        {'SMILES': None}
        >>> client.close()
        """
        if not cid:
            return {p: None for p in props}
        base = "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid"
        url = f"{base}/{cid}/property/{','.join(props)}/JSON"
        for k in range(self.retries):
            try:
                r = self._session.get(url, timeout=12)
                r.raise_for_status()
                row = r.json()["PropertyTable"]["Properties"][0]
                time.sleep(self.sleep)
                return {p: row.get(p) for p in props}
            except Exception as e:
                if k + 1 == self.retries:
                    self.log(f"[PubChem] CID {cid}: {e}")
                    return {p: None for p in props}
                time.sleep(self.sleep * (2 ** k))
        return {p: None for p in props}

    def close(self) -> None:
        """
        Close the underlying HTTP session.

        Should be called when the client is no longer needed to release
        connection resources.

        Examples
        --------
        >>> client = PubChemClient()
        >>> client.close()
        """
        self._session.close()
