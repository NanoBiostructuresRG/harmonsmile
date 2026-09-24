# SPDX-License-Identifier: LGPL-3.0-or-later
"""Unit tests for harmonsmile.pubchem."""

from unittest.mock import MagicMock, patch

import pytest

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

    @pytest.mark.parametrize("cid", [None, "", "not-a-cid"])
    def test_missing_or_invalid_cid_is_not_attempted(self, cid):
        """Missing or invalid CIDs preserve that no request was attempted."""
        client = _PubChemClient()
        with patch.object(client._session, "get") as mock_get:
            result = client.fetch_props(cid, ["SMILES", "MolecularWeight"])

        assert result.status == "not_attempted"
        assert result.properties == {"SMILES": None, "MolecularWeight": None}
        assert result.message == "PubChem acquisition not attempted: missing or invalid CID"
        mock_get.assert_not_called()
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
        with (
            patch.object(client._session, "get", return_value=mock_response) as mock_get,
            patch("harmonsmile.pubchem.time.sleep") as mock_sleep,
        ):
            result = client.fetch_props("702", ["SMILES", "MolecularWeight"])

        assert result.status == "ok"
        assert result.message is None
        assert result.properties == {"SMILES": "CCO", "MolecularWeight": 46.07}
        mock_get.assert_called_once()
        mock_sleep.assert_called_once_with(0.1)
        client.close()

    def test_successful_fetch_with_absent_smiles_remains_ok(self):
        """An absent requested property is distinct from acquisition failure."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"PropertyTable": {"Properties": [{}]}}

        client = _PubChemClient(sleep=0.1)
        with (
            patch.object(client._session, "get", return_value=mock_response) as mock_get,
            patch("harmonsmile.pubchem.time.sleep"),
        ):
            result = client.fetch_props("702", ["SMILES"])

        assert result.status == "ok"
        assert result.message is None
        assert result.properties == {"SMILES": None}
        mock_get.assert_called_once()
        client.close()

    def test_failed_fetch_preserves_exhausted_acquisition(self):
        """Final acquisition failure retains a diagnostic and attempt count."""
        client = _PubChemClient(sleep=0.1, retries=2)
        failures = [Exception("first failure"), Exception("final timeout")]
        with (
            patch.object(client._session, "get", side_effect=failures) as mock_get,
            patch("harmonsmile.pubchem.time.sleep"),
        ):
            result = client.fetch_props("999999999", ["SMILES"])

        assert result.status == "failed"
        assert result.properties == {"SMILES": None}
        assert result.message == "PubChem acquisition failed: Exception: final timeout"
        assert mock_get.call_count == 2
        client.close()

    def test_fetch_recovers_before_attempt_budget_is_exhausted(self):
        """A later successful attempt determines the final acquisition result."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "PropertyTable": {"Properties": [{"SMILES": "CCO"}]}
        }
        client = _PubChemClient(sleep=0.1, retries=3)
        with (
            patch.object(
                client._session,
                "get",
                side_effect=[Exception("temporary failure"), mock_response],
            ) as mock_get,
            patch("harmonsmile.pubchem.time.sleep"),
        ):
            result = client.fetch_props("702", ["SMILES"])

        assert result.status == "ok"
        assert result.properties == {"SMILES": "CCO"}
        assert result.message is None
        assert mock_get.call_count == 2
        client.close()

    def test_failed_attempt_backoff_is_unchanged(self):
        """Three failed attempts retain the existing 0.2/0.4 second backoff."""
        client = _PubChemClient()
        with (
            patch.object(client._session, "get", side_effect=Exception("timeout")) as mock_get,
            patch("harmonsmile.pubchem.time.sleep") as mock_sleep,
        ):
            result = client.fetch_props("999999999", ["SMILES"])

        assert result.status == "failed"
        assert mock_get.call_count == 3
        assert [call.args[0] for call in mock_sleep.call_args_list] == [0.2, 0.4]
        client.close()

    def test_close(self):
        """close() does not raise."""
        client = _PubChemClient()
        client.close()
