# SPDX-License-Identifier: LGPL-3.0-or-later
"""
ChEMBL REST API client for harmonsmile.

Provides :class:`_ChEMBLClient` for fetching compound properties from the
ChEMBL REST API, with exponential backoff and persistent connection reuse.
"""

from __future__ import annotations

import logging
import re
import time
from collections.abc import Callable
from typing import Any

import requests

_CHEMBL_ID_RE = re.compile(r"^CHEMBL\d+$")

_ROOT_FIELDS: tuple[str, ...] = ("molecule_chembl_id", "pref_name")
_STRUCT_FIELDS: tuple[str, ...] = ("canonical_smiles", "standard_inchi", "standard_inchi_key")
_PROP_FIELDS: tuple[str, ...] = (
    "alogp", "full_mwt", "full_molformula",
    "hba", "hbd", "heavy_atoms",
    "psa", "qed_weighted", "num_ro5_violations", "rtb",
)
_ALL_FIELDS: tuple[str, ...] = _ROOT_FIELDS + _STRUCT_FIELDS + _PROP_FIELDS


class _ChEMBLClient:
    """
    Client for fetching compound properties from the ChEMBL REST API.

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
    >>> client = _ChEMBLClient()
    >>> props = client.fetch_props("CHEMBL25")  # doctest: +SKIP
    >>> client.close()
    """

    _BASE_URL = "https://www.ebi.ac.uk/chembl/api/data/molecule"

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

    def fetch_props(self, chembl_id: str | None) -> dict[str, Any]:
        """
        Fetch compound properties from ChEMBL by ChEMBL ID.

        Parameters
        ----------
        chembl_id : str or None
            ChEMBL compound identifier (e.g. 'CHEMBL25'). Whitespace is
            stripped; IDs not matching ``CHEMBL\\d+`` return all-None values.

        Returns
        -------
        dict[str, Any]
            Dictionary of 15 extracted properties. Values are None if the
            fetch failed or the identifier is missing or invalid.

        Examples
        --------
        >>> client = _ChEMBLClient()
        >>> client.fetch_props("CHEMBL25")  # doctest: +SKIP
        {'molecule_chembl_id': 'CHEMBL25', 'pref_name': 'ASPIRIN', ...}
        >>> client.fetch_props("")
        {'molecule_chembl_id': None, 'pref_name': None, ...}
        >>> client.close()
        """
        null = {f: None for f in _ALL_FIELDS}
        if not chembl_id:
            return null
        chembl_id = str(chembl_id).strip()
        if not _CHEMBL_ID_RE.match(chembl_id):
            return null
        url = f"{self._BASE_URL}/{chembl_id}.json"
        for k in range(self.retries):
            try:
                r = self._session.get(url, timeout=12)
                r.raise_for_status()
                data = r.json()
                structs = data.get("molecule_structures") or {}
                props = data.get("molecule_properties") or {}
                result: dict[str, Any] = {
                    "molecule_chembl_id": data.get("molecule_chembl_id"),
                    "pref_name":          data.get("pref_name"),
                    "canonical_smiles":   structs.get("canonical_smiles"),
                    "standard_inchi":     structs.get("standard_inchi"),
                    "standard_inchi_key": structs.get("standard_inchi_key"),
                    "alogp":              props.get("alogp"),
                    "full_mwt":           props.get("full_mwt"),
                    "full_molformula":    props.get("full_molformula"),
                    "hba":                props.get("hba"),
                    "hbd":                props.get("hbd"),
                    "heavy_atoms":        props.get("heavy_atoms"),
                    "psa":                props.get("psa"),
                    "qed_weighted":       props.get("qed_weighted"),
                    "num_ro5_violations": props.get("num_ro5_violations"),
                    "rtb":                props.get("rtb"),
                }
                time.sleep(self.sleep)
                return result
            except Exception as e:
                if k + 1 == self.retries:
                    self.log(f"[ChEMBL] {chembl_id}: {e}")
                    return null
                time.sleep(self.sleep * (2 ** k))
        return null

    def __enter__(self) -> _ChEMBLClient:
        """
        Enter the context manager.

        Returns
        -------
        _ChEMBLClient
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
        >>> client = _ChEMBLClient()
        >>> client.close()
        """
        self._session.close()
