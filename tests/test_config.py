# SPDX-License-Identifier: LGPL-3.0-or-later
"""Unit tests for harmonsmile.config."""

import pytest
from harmonsmile import Config


class TestConfig:
    """Tests for Config dataclass."""

    def test_minimal_creation(self):
        """Config can be created with only required fields."""
        cfg = Config(input_path="data/in.csv", output_path="results/out.csv")
        assert cfg.input_path == "data/in.csv"
        assert cfg.output_path == "results/out.csv"

    def test_defaults(self):
        """Default values are set correctly."""
        cfg = Config(input_path="data/in.csv", output_path="results/out.csv")
        assert cfg.error_log == "logs/errors.txt"
        assert cfg.cid_col == "PubChem CID"
        assert cfg.props == ("SMILES", "ConnectivitySMILES", "MolecularFormula",
                            "MolecularWeight", "InChI", "InChIKey", "XLogP", "TPSA",
                            "Charge", "HBondDonorCount", "HBondAcceptorCount",
                            "RotatableBondCount", "HeavyAtomCount",)

    def test_custom_values(self):
        """Custom values override defaults."""
        cfg = Config(
            input_path="data/in.csv",
            output_path="results/out.csv",
            cid_col="CID",
            props=("SMILES",),
        )
        assert cfg.cid_col == "CID"
        assert cfg.props == ("SMILES",)

    def test_frozen(self):
        """Config is immutable after creation."""
        cfg = Config(input_path="data/in.csv", output_path="results/out.csv")
        with pytest.raises(Exception):
            cfg.input_path = "other.csv"

    def test_empty_input_path_raises(self):
        """Empty input_path raises ValueError."""
        with pytest.raises(ValueError, match="input_path"):
            Config(input_path="", output_path="results/out.csv")

    def test_empty_output_path_raises(self):
        """Empty output_path raises ValueError."""
        with pytest.raises(ValueError, match="output_path"):
            Config(input_path="data/in.csv", output_path="")

    def test_empty_props_raises(self):
        """Empty props tuple raises ValueError."""
        with pytest.raises(ValueError, match="props"):
            Config(input_path="data/in.csv", output_path="results/out.csv", props=())
