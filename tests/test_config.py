# SPDX-License-Identifier: LGPL-3.0-or-later
"""Unit tests for harmonsmile.config."""

import pytest
from harmonsmile import PubChemConfig, ChEMBLConfig, SMILESConfig


class TestPubChemConfig:
    """Tests for PubChemConfig dataclass."""

    def test_minimal_creation(self):
        """PubChemConfig can be created with only required fields."""
        cfg = PubChemConfig(input_path="data/in.csv", output_path="results/out.csv")
        assert cfg.input_path == "data/in.csv"
        assert cfg.output_path == "results/out.csv"

    def test_defaults(self):
        """Default values are set correctly."""
        cfg = PubChemConfig(input_path="data/in.csv", output_path="results/out.csv")
        assert cfg.error_log == "logs/errors.txt"
        assert cfg.cid_col == "PubChem CID"
        assert cfg.props == (
            "SMILES", "ConnectivitySMILES", "MolecularFormula",
            "MolecularWeight", "InChI", "InChIKey", "XLogP", "TPSA",
            "Charge", "HBondDonorCount", "HBondAcceptorCount",
            "RotatableBondCount", "HeavyAtomCount",
        )

    def test_custom_values(self):
        """Custom values override defaults."""
        cfg = PubChemConfig(
            input_path="data/in.csv",
            output_path="results/out.csv",
            cid_col="CID",
            props=("SMILES",),
        )
        assert cfg.cid_col == "CID"
        assert cfg.props == ("SMILES",)

    def test_frozen(self):
        """PubChemConfig is immutable after creation."""
        cfg = PubChemConfig(input_path="data/in.csv", output_path="results/out.csv")
        with pytest.raises(Exception):
            cfg.input_path = "other.csv"

    def test_empty_input_path_raises(self):
        """Empty input_path raises ValueError."""
        with pytest.raises(ValueError, match="input_path"):
            PubChemConfig(input_path="", output_path="results/out.csv")

    def test_input_path_traversal_raises(self):
        """input_path with '..' raises ValueError."""
        with pytest.raises(ValueError, match="traversal"):
            PubChemConfig(input_path="../../etc/passwd", output_path="results/out.csv")

    def test_empty_output_path_raises(self):
        """Empty output_path raises ValueError."""
        with pytest.raises(ValueError, match="output_path"):
            PubChemConfig(input_path="data/in.csv", output_path="")

    def test_empty_props_raises(self):
        """Empty props tuple raises ValueError."""
        with pytest.raises(ValueError, match="props"):
            PubChemConfig(input_path="data/in.csv", output_path="results/out.csv", props=())

    def test_empty_cid_col_raises(self):
        """Empty cid_col raises ValueError."""
        with pytest.raises(ValueError, match="cid_col"):
            PubChemConfig(input_path="data/in.csv", output_path="results/out.csv", cid_col="")

    def test_whitespace_cid_col_raises(self):
        """Whitespace-only cid_col raises ValueError."""
        with pytest.raises(ValueError, match="cid_col"):
            PubChemConfig(input_path="data/in.csv", output_path="results/out.csv", cid_col="   ")


class TestChEMBLConfig:
    """Tests for ChEMBLConfig dataclass."""

    def test_minimal_creation(self):
        """ChEMBLConfig can be created with only required fields."""
        cfg = ChEMBLConfig(input_path="data/in.csv", output_path="results/out.csv")
        assert cfg.input_path == "data/in.csv"
        assert cfg.output_path == "results/out.csv"

    def test_defaults(self):
        """Default values are set correctly."""
        cfg = ChEMBLConfig(input_path="data/in.csv", output_path="results/out.csv")
        assert cfg.chembl_id_col == "ChEMBL ID"
        assert cfg.error_log == "logs/errors.txt"

    def test_custom_chembl_id_col(self):
        """Custom chembl_id_col overrides default."""
        cfg = ChEMBLConfig(
            input_path="data/in.csv",
            output_path="results/out.csv",
            chembl_id_col="ID",
        )
        assert cfg.chembl_id_col == "ID"

    def test_frozen(self):
        """ChEMBLConfig is immutable after creation."""
        cfg = ChEMBLConfig(input_path="data/in.csv", output_path="results/out.csv")
        with pytest.raises(Exception):
            cfg.input_path = "other.csv"

    def test_empty_input_path_raises(self):
        """Empty input_path raises ValueError."""
        with pytest.raises(ValueError, match="input_path"):
            ChEMBLConfig(input_path="", output_path="results/out.csv")

    def test_input_path_traversal_raises(self):
        """input_path with '..' raises ValueError."""
        with pytest.raises(ValueError, match="traversal"):
            ChEMBLConfig(input_path="../../etc/passwd", output_path="results/out.csv")

    def test_empty_output_path_raises(self):
        """Empty output_path raises ValueError."""
        with pytest.raises(ValueError, match="output_path"):
            ChEMBLConfig(input_path="data/in.csv", output_path="")

    def test_output_path_traversal_raises(self):
        """output_path with '..' raises ValueError."""
        with pytest.raises(ValueError, match="traversal"):
            ChEMBLConfig(input_path="data/in.csv", output_path="../../etc/malicious")

    def test_empty_chembl_id_col_raises(self):
        """Empty chembl_id_col raises ValueError."""
        with pytest.raises(ValueError, match="chembl_id_col"):
            ChEMBLConfig(input_path="data/in.csv", output_path="results/out.csv", chembl_id_col="")

    def test_whitespace_chembl_id_col_raises(self):
        """Whitespace-only chembl_id_col raises ValueError."""
        with pytest.raises(ValueError, match="chembl_id_col"):
            ChEMBLConfig(input_path="data/in.csv", output_path="results/out.csv", chembl_id_col="   ")


class TestSMILESConfig:
    """Tests for SMILESConfig dataclass."""

    def test_minimal_creation(self):
        """SMILESConfig can be created with required fields."""
        cfg = SMILESConfig(
            input_path="data/in.csv",
            output_path="results/out.csv",
            smiles_col="SMILES",
        )
        assert cfg.input_path == "data/in.csv"
        assert cfg.output_path == "results/out.csv"
        assert cfg.smiles_col == "SMILES"

    def test_defaults(self):
        """Default error_log is set correctly."""
        cfg = SMILESConfig(
            input_path="data/in.csv",
            output_path="results/out.csv",
            smiles_col="SMILES",
        )
        assert cfg.error_log == "logs/errors.txt"

    def test_custom_smiles_col(self):
        """Custom smiles_col is stored correctly."""
        cfg = SMILESConfig(
            input_path="data/in.csv",
            output_path="results/out.csv",
            smiles_col="canonical_smiles",
        )
        assert cfg.smiles_col == "canonical_smiles"

    def test_frozen(self):
        """SMILESConfig is immutable after creation."""
        cfg = SMILESConfig(
            input_path="data/in.csv",
            output_path="results/out.csv",
            smiles_col="SMILES",
        )
        with pytest.raises(Exception):
            cfg.input_path = "other.csv"

    def test_empty_input_path_raises(self):
        """Empty input_path raises ValueError."""
        with pytest.raises(ValueError, match="input_path"):
            SMILESConfig(input_path="", output_path="results/out.csv", smiles_col="SMILES")

    def test_input_path_traversal_raises(self):
        """input_path with '..' raises ValueError."""
        with pytest.raises(ValueError, match="traversal"):
            SMILESConfig(input_path="../../etc/passwd", output_path="results/out.csv", smiles_col="SMILES")

    def test_empty_output_path_raises(self):
        """Empty output_path raises ValueError."""
        with pytest.raises(ValueError, match="output_path"):
            SMILESConfig(input_path="data/in.csv", output_path="", smiles_col="SMILES")

    def test_output_path_traversal_raises(self):
        """output_path with '..' raises ValueError."""
        with pytest.raises(ValueError, match="traversal"):
            SMILESConfig(input_path="data/in.csv", output_path="../../etc/malicious", smiles_col="SMILES")

    def test_empty_smiles_col_raises(self):
        """Empty smiles_col raises ValueError."""
        with pytest.raises(ValueError, match="smiles_col"):
            SMILESConfig(input_path="data/in.csv", output_path="results/out.csv", smiles_col="")

    def test_whitespace_smiles_col_raises(self):
        """Whitespace-only smiles_col raises ValueError."""
        with pytest.raises(ValueError, match="smiles_col"):
            SMILESConfig(input_path="data/in.csv", output_path="results/out.csv", smiles_col="   ")
