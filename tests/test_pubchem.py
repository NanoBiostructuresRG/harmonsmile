# SPDX-License-Identifier: LGPL-3.0-or-later
"""Unit tests for harmonsmile.pubchem."""

import pytest
from unittest.mock import MagicMock, patch
from harmonsmile.pubchem import _PubChemClient


class TestPubChemClientInit:
    """Tests for internal PubChem client initialization."""

    def test_default_values(self):
        """Default sleep and retries are set correctly."""
        client = _PubChemClient()
        assert client.sleep == 0.2
        assert client.retries == 3
        client.close()

    def test_custom_values(self):
        """Custom sleep and retries are set correctly."""
        client = _PubChemClient(sleep=0.5, retries=5)
        assert client.sleep == 0.5
        assert client.retries == 5
        client.close()

    def test_session_user_agent(self):
        """Session User-Agent is set to harmonsmile."""
        client = _PubChemClient()
        assert "harmonsmile" in client._session.headers["User-Agent"]
        client.close()


class TestFetchProps:
    """Tests for internal PubChem client fetch_props."""

    def test_empty_cid_returns_none_values(self):
        """Empty CID returns dict with None values without network call."""
        client = _PubChemClient()
        result = client.fetch_props("", ["SMILES", "MolecularWeight"])
        assert result == {"SMILES": None, "MolecularWeight": None}
        client.close()

    def test_none_cid_returns_none_values(self):
        """None CID returns dict with None values."""
        client = _PubChemClient()
        result = client.fetch_props(None, ["SMILES"])
        assert result == {"SMILES": None}
        client.close()

    def test_successful_fetch(self):
        """Successful API response returns property values."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "PropertyTable": {
                "Properties": [{"SMILES": "CCO", "MolecularWeight": 46.07}]
            }
        }
        mock_response.raise_for_status = MagicMock()

        client = _PubChemClient(sleep=0.1)
        with patch.object(client._session, "get", return_value=mock_response):
            result = client.fetch_props("702", ["SMILES", "MolecularWeight"])

        assert result["SMILES"] == "CCO"
        assert result["MolecularWeight"] == 46.07
        client.close()

    def test_failed_fetch_returns_none_values(self):
        """Failed fetch after all retries returns None values."""
        client = _PubChemClient(sleep=0.1, retries=2)
        with patch.object(client._session, "get", side_effect=Exception("timeout")):
            result = client.fetch_props("999999999", ["SMILES"], )

        assert result == {"SMILES": None}
        client.close()

    def test_close(self):
        """close() does not raise."""
        client = _PubChemClient()
        client.close()
