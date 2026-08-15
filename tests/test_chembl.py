# SPDX-License-Identifier: LGPL-3.0-or-later
"""Unit tests for harmonsmile.chembl."""

from unittest.mock import MagicMock, patch

import pytest

from harmonsmile.chembl import _ChEMBLClient

_MOCK_RESPONSE = {
    "molecule_chembl_id": "CHEMBL25",
    "pref_name": "ASPIRIN",
    "molecule_structures": {
        "canonical_smiles": "CC(=O)Oc1ccccc1C(=O)O",
        "standard_inchi": "InChI=1S/C9H8O4/c1-6(10)13-8-4-2-3-5-7(8)9(11)12/h2-5H,1H3,(H,11,12)",
        "standard_inchi_key": "BSYNRYMUTXBXSQ-UHFFFAOYSA-N",
    },
    "molecule_properties": {
        "alogp": "1.31",
        "full_mwt": "180.16",
        "full_molformula": "C9H8O4",
        "hba": "3",
        "hbd": "1",
        "heavy_atoms": 13,
        "psa": "63.60",
        "qed_weighted": "0.55",
        "num_ro5_violations": 0,
        "rtb": 3,
    },
}


class TestChEMBLClientInit:
    """Tests for _ChEMBLClient initialization."""

    def test_default_values(self):
        """Default sleep and retries are set correctly."""
        client = _ChEMBLClient()
        assert client.sleep == 0.2
        assert client.retries == 3
        client.close()

    def test_custom_values(self):
        """Custom sleep and retries are set correctly."""
        client = _ChEMBLClient(sleep=0.5, retries=5)
        assert client.sleep == 0.5
        assert client.retries == 5
        client.close()

    def test_session_user_agent(self):
        """Session User-Agent is set to harmonsmile."""
        client = _ChEMBLClient()
        assert "harmonsmile" in client._session.headers["User-Agent"]
        client.close()


class TestFetchProps:
    """Tests for _ChEMBLClient.fetch_props."""

    def test_empty_id_returns_none_values(self):
        """Empty ChEMBL ID returns dict with None values without a network call."""
        client = _ChEMBLClient()
        result = client.fetch_props("")
        assert all(v is None for v in result.values())
        assert "canonical_smiles" in result
        assert "full_mwt" in result
        client.close()

    def test_none_id_returns_none_values(self):
        """None ChEMBL ID returns dict with None values."""
        client = _ChEMBLClient()
        result = client.fetch_props(None)
        assert all(v is None for v in result.values())
        client.close()

    def test_invalid_format_returns_none_values(self):
        """ChEMBL ID not matching CHEMBL\\d+ returns None values without a network call."""
        client = _ChEMBLClient()
        result = client.fetch_props("NOTCHEMBL")
        assert all(v is None for v in result.values())
        client.close()

    def test_successful_fetch(self):
        """Successful API response returns all property values."""
        mock_response = MagicMock()
        mock_response.json.return_value = _MOCK_RESPONSE
        mock_response.raise_for_status = MagicMock()

        client = _ChEMBLClient(sleep=0.1)
        with patch.object(client._session, "get", return_value=mock_response):
            result = client.fetch_props("CHEMBL25")

        assert result["molecule_chembl_id"] == "CHEMBL25"
        assert result["pref_name"] == "ASPIRIN"
        assert result["canonical_smiles"] == "CC(=O)Oc1ccccc1C(=O)O"
        assert result["standard_inchi_key"] == "BSYNRYMUTXBXSQ-UHFFFAOYSA-N"
        assert result["full_mwt"] == "180.16"
        assert result["full_molformula"] == "C9H8O4"
        assert result["alogp"] == "1.31"
        assert result["heavy_atoms"] == 13
        client.close()

    def test_failed_fetch_returns_none_values(self):
        """Failed fetch after all retries returns None values."""
        client = _ChEMBLClient(sleep=0.1, retries=2)
        with patch.object(client._session, "get", side_effect=Exception("timeout")):
            result = client.fetch_props("CHEMBL25")

        assert all(v is None for v in result.values())
        client.close()

    def test_close(self):
        """close() does not raise."""
        client = _ChEMBLClient()
        client.close()


class TestChEMBLClientSecurity:
    """Security tests for _ChEMBLClient validation."""

    def test_sleep_below_minimum_rejected(self):
        """sleep below 0.1 raises ValueError."""
        with pytest.raises(ValueError, match="sleep"):
            _ChEMBLClient(sleep=0.0)

    def test_sleep_above_maximum_rejected(self):
        """sleep above 10.0 raises ValueError."""
        with pytest.raises(ValueError, match="sleep"):
            _ChEMBLClient(sleep=11.0)

    def test_retries_below_minimum_rejected(self):
        """retries below 1 raises ValueError."""
        with pytest.raises(ValueError, match="retries"):
            _ChEMBLClient(retries=0)

    def test_retries_above_maximum_rejected(self):
        """retries above 10 raises ValueError."""
        with pytest.raises(ValueError, match="retries"):
            _ChEMBLClient(retries=11)

    def test_invalid_chembl_id_format_returns_none(self):
        """IDs not matching CHEMBL\\d+ return None values without a network call."""
        client = _ChEMBLClient()
        for bad_id in ("chembl25", "12345", "CHEMBL", "../../etc/passwd", "CHEMBL-25"):
            result = client.fetch_props(bad_id)
            assert all(v is None for v in result.values()), f"Expected all None for ID {bad_id!r}"
        client.close()

    def test_valid_bounds_accepted(self):
        """Valid sleep and retries values are accepted."""
        client = _ChEMBLClient(sleep=0.5, retries=5)
        assert client.sleep == 0.5
        assert client.retries == 5
        client.close()
