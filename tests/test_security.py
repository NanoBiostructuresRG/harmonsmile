# SPDX-License-Identifier: LGPL-3.0-or-later
"""Security validation tests for harmonsmile."""

import pytest
from harmonsmile import Config
from harmonsmile.pubchem import PubChemClient


class TestConfigSecurity:
    """Security tests for Config validation."""

    def test_path_traversal_rejected(self):
        """output_path with '..' raises ValueError."""
        with pytest.raises(ValueError, match="traversal"):
            Config(
                input_path="data/in.csv",
                output_path="../../etc/cron.d/malicious",
            )

    def test_invalid_pubchem_prop_rejected(self):
        """Unknown PubChem property raises ValueError."""
        with pytest.raises(ValueError, match="Invalid PubChem properties"):
            Config(
                input_path="data/in.csv",
                output_path="results/out.csv",
                props=("SMILES", "../../../etc"),
            )

    def test_multiple_invalid_props_listed(self):
        """All invalid properties are listed in the error message."""
        with pytest.raises(ValueError, match="Invalid PubChem properties"):
            Config(
                input_path="data/in.csv",
                output_path="results/out.csv",
                props=("FakeProp1", "FakeProp2"),
            )

    def test_valid_props_accepted(self):
        """All whitelisted properties are accepted."""
        cfg = Config(
            input_path="data/in.csv",
            output_path="results/out.csv",
            props=("SMILES", "MolecularWeight", "InChIKey", "XLogP"),
        )
        assert cfg.props == ("SMILES", "MolecularWeight", "InChIKey", "XLogP")

    def test_normal_output_path_accepted(self):
        """Normal output path without traversal is accepted."""
        cfg = Config(
            input_path="data/in.csv",
            output_path="results/subdir/out.csv",
        )
        assert cfg.output_path == "results/subdir/out.csv"


class TestPubChemClientSecurity:
    """Security tests for PubChemClient validation."""

    def test_sleep_below_minimum_rejected(self):
        """sleep below 0.1 raises ValueError."""
        with pytest.raises(ValueError, match="sleep"):
            PubChemClient(sleep=0.0)

    def test_sleep_above_maximum_rejected(self):
        """sleep above 10.0 raises ValueError."""
        with pytest.raises(ValueError, match="sleep"):
            PubChemClient(sleep=11.0)

    def test_retries_below_minimum_rejected(self):
        """retries below 1 raises ValueError."""
        with pytest.raises(ValueError, match="retries"):
            PubChemClient(retries=0)

    def test_retries_above_maximum_rejected(self):
        """retries above 10 raises ValueError."""
        with pytest.raises(ValueError, match="retries"):
            PubChemClient(retries=11)

    def test_cid_injection_stripped(self):
        """Non-numeric characters in CID are stripped before URL construction."""
        client = PubChemClient()
        # CID with injection attempt — non-digits stripped, empty result → None values
        result = client.fetch_props("123/property/SMILES/JSON?fake=true", ["SMILES"])
        # After stripping non-digits: "123" — valid CID, real network call skipped via check
        # We only verify no exception is raised and result is a dict
        assert isinstance(result, dict)
        assert "SMILES" in result
        client.close()

    def test_fully_non_numeric_cid_returns_none(self):
        """CID with no digits returns None values without network call."""
        client = PubChemClient()
        result = client.fetch_props("../../etc/passwd", ["SMILES"])
        assert result == {"SMILES": None}
        client.close()

    def test_valid_bounds_accepted(self):
        """Valid sleep and retries values are accepted."""
        client = PubChemClient(sleep=0.5, retries=5)
        assert client.sleep == 0.5
        assert client.retries == 5
        client.close()
