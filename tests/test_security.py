# SPDX-License-Identifier: LGPL-3.0-or-later
"""Security validation tests for harmonsmile."""

from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from harmonsmile import ChEMBLConfig, PubChemConfig, SMILESConfig
from harmonsmile.io import save_table
from harmonsmile.pubchem import _PubChemClient


class TestPubChemConfigSecurity:
    """Security tests for PubChemConfig validation."""

    def test_input_path_traversal_rejected(self):
        """input_path with '..' raises ValueError."""
        with pytest.raises(ValueError, match="traversal"):
            PubChemConfig(input_path="../../etc/passwd")

    def test_invalid_pubchem_prop_rejected(self):
        """Unknown PubChem property raises ValueError."""
        with pytest.raises(ValueError, match="Invalid PubChem properties"):
            PubChemConfig(
                input_path="data/in.csv",
                props=("SMILES", "../../../etc"),
            )

    def test_multiple_invalid_props_listed(self):
        """All invalid properties are listed in the error message."""
        with pytest.raises(ValueError, match="Invalid PubChem properties"):
            PubChemConfig(
                input_path="data/in.csv",
                props=("FakeProp1", "FakeProp2"),
            )

    def test_valid_props_accepted(self):
        """All whitelisted properties are accepted."""
        cfg = PubChemConfig(
            input_path="data/in.csv",
            props=("SMILES", "MolecularWeight", "InChIKey", "XLogP"),
        )
        assert cfg.props == ("SMILES", "MolecularWeight", "InChIKey", "XLogP")

    def test_normal_paths_accepted(self):
        """Normal paths without traversal are accepted."""
        cfg = PubChemConfig(input_path="data/in.csv")
        assert cfg.input_path == "data/in.csv"


class TestChEMBLConfigSecurity:
    """Security tests for ChEMBLConfig validation."""

    def test_input_path_traversal_rejected(self):
        """input_path with '..' raises ValueError."""
        with pytest.raises(ValueError, match="traversal"):
            ChEMBLConfig(input_path="../../etc/passwd")

    def test_normal_paths_accepted(self):
        """Normal paths without traversal are accepted."""
        cfg = ChEMBLConfig(input_path="data/in.csv")
        assert cfg.input_path == "data/in.csv"


class TestSMILESConfigSecurity:
    """Security tests for SMILESConfig validation."""

    def test_input_path_traversal_rejected(self):
        """input_path with '..' raises ValueError."""
        with pytest.raises(ValueError, match="traversal"):
            SMILESConfig(
                input_path="../../etc/passwd",
                smiles_col="SMILES",
            )

    def test_normal_paths_accepted(self):
        """Normal paths without traversal are accepted."""
        cfg = SMILESConfig(
            input_path="data/in.csv",
            smiles_col="SMILES",
        )
        assert cfg.input_path == "data/in.csv"


class TestSaveTableSecurity:
    """Security tests for the package write boundary."""

    def test_output_path_traversal_rejected(self):
        with pytest.raises(ValueError, match="traversal"):
            save_table(pd.DataFrame({"a": [1]}), "../../etc/cron.d/malicious")


class TestPubChemClientSecurity:
    """Security tests for internal PubChem client validation."""

    def test_sleep_below_minimum_rejected(self):
        """sleep below 0.1 raises ValueError."""
        with pytest.raises(ValueError, match="sleep"):
            _PubChemClient(sleep=0.0)

    def test_sleep_above_maximum_rejected(self):
        """sleep above 10.0 raises ValueError."""
        with pytest.raises(ValueError, match="sleep"):
            _PubChemClient(sleep=11.0)

    def test_retries_below_minimum_rejected(self):
        """retries below 1 raises ValueError."""
        with pytest.raises(ValueError, match="retries"):
            _PubChemClient(retries=0)

    def test_retries_above_maximum_rejected(self):
        """retries above 10 raises ValueError."""
        with pytest.raises(ValueError, match="retries"):
            _PubChemClient(retries=11)

    def test_cid_injection_stripped(self):
        """Non-numeric characters in CID are stripped before URL construction."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "PropertyTable": {"Properties": [{"SMILES": "CCO"}]}
        }
        mock_response.raise_for_status = MagicMock()

        client = _PubChemClient(sleep=0.1)
        with patch.object(client._session, "get", return_value=mock_response) as mock_get:
            result = client.fetch_props("123/property/SMILES/JSON?fake=true", ["SMILES"])

        called_url = mock_get.call_args[0][0]
        assert "/123/" in called_url
        assert "fake" not in called_url
        assert result == {"SMILES": "CCO"}
        client.close()

    def test_fully_non_numeric_cid_returns_none(self):
        """CID with no digits returns None values without network call."""
        client = _PubChemClient()
        result = client.fetch_props("../../etc/passwd", ["SMILES"])
        assert result == {"SMILES": None}
        client.close()

    def test_valid_bounds_accepted(self):
        """Valid sleep and retries values are accepted."""
        client = _PubChemClient(sleep=0.5, retries=5)
        assert client.sleep == 0.5
        assert client.retries == 5
        client.close()
