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


class _PubChemClient:
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
        if not 0.1 <= sleep <= 10.0:
            raise ValueError("sleep must be between 0.1 and 10.0 seconds.")
        if not 1 <= retries <= 10:
            raise ValueError("retries must be between 1 and 10.")
        self.log = logger or (lambda m: logging.getLogger(__name__).warning(m))
        self.sleep = sleep
        self.retries = retries
        self._session = requests.Session()
        self._session.headers.update({"User-Agent": "harmonsmile (python-requests)"})

    def fetch_props(self, cid: str | None, props: list[str]) -> dict[str, Any]:
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
        >>> client.fetch_props("2723949", ["SMILES", "MolecularWeight"])  # doctest: +SKIP
        {'SMILES': 'CC(=S)N', 'MolecularWeight': '74.15'}
        >>> client.fetch_props("", ["SMILES"])
        {'SMILES': None}
        >>> client.close()
        """
        if not cid:
            return {p: None for p in props}
        cid = "".join(ch for ch in str(cid) if ch.isdigit())
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

    def __enter__(self) -> _PubChemClient:
        """
        Enter the context manager.

        Returns
        -------
        PubChemClient
            The client instance itself.
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        """
        Exit the context manager and release resources.

        Parameters
        ----------
        exc_type : type or None
            Exception type, if any.
        exc_val : BaseException or None
            Exception value, if any.
        exc_tb : traceback or None
            Exception traceback, if any.

        Returns
        -------
        bool
            Always False; exceptions are not suppressed.
        """
        self.close()
        return False

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


# Deprecated alias — will be removed in a future release
PubChemClient = _PubChemClient
