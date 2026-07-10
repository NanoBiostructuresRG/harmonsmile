# SPDX-License-Identifier: LGPL-3.0-or-later
"""Unit tests for harmonsmile.config."""

import pytest
from harmonsmile import PubChemConfig, ChEMBLConfig, SMILESConfig


class TestPubChemConfig:
    """Tests for PubChemConfig dataclass."""

    def test_minimal_creation(self):
        cfg = PubChemConfig(input_path="data/in.csv")
        assert cfg.input_path == "data/in.csv"

    def test_defaults(self):
        cfg = PubChemConfig(input_path="data/in.csv")
        assert cfg.cid_col is None
        assert cfg.keep_extra_columns is False
        assert cfg.props == (
            "SMILES", "ConnectivitySMILES", "MolecularFormula",
            "MolecularWeight", "InChI", "InChIKey", "XLogP", "TPSA",
            "Charge", "HBondDonorCount", "HBondAcceptorCount",
            "RotatableBondCount", "HeavyAtomCount",
        )

    def test_custom_values(self):
        cfg = PubChemConfig(
            input_path="data/in.csv",
            cid_col="CID",
            props=("SMILES",),
            keep_extra_columns=True,
        )
        assert cfg.cid_col == "CID"
        assert cfg.props == ("SMILES",)
        assert cfg.keep_extra_columns is True

    def test_frozen(self):
        cfg = PubChemConfig(input_path="data/in.csv")
        with pytest.raises(Exception):
            cfg.input_path = "other.csv"

    def test_empty_input_path_raises(self):
        with pytest.raises(ValueError, match="input_path"):
            PubChemConfig(input_path="")

    def test_input_path_traversal_raises(self):
        with pytest.raises(ValueError, match="traversal"):
            PubChemConfig(input_path="../../etc/passwd")

    def test_empty_props_raises(self):
        with pytest.raises(ValueError, match="props"):
            PubChemConfig(input_path="data/in.csv", props=())

    def test_empty_cid_col_raises(self):
        with pytest.raises(ValueError, match="cid_col"):
            PubChemConfig(input_path="data/in.csv", cid_col="")

    def test_whitespace_cid_col_raises(self):
        with pytest.raises(ValueError, match="cid_col"):
            PubChemConfig(input_path="data/in.csv", cid_col="   ")

    def test_keep_extra_columns_must_be_bool(self):
        with pytest.raises(ValueError, match="keep_extra_columns"):
            PubChemConfig(input_path="data/in.csv", keep_extra_columns="yes")


class TestChEMBLConfig:
    """Tests for ChEMBLConfig dataclass."""

    def test_minimal_creation(self):
        cfg = ChEMBLConfig(input_path="data/in.csv")
        assert cfg.input_path == "data/in.csv"

    def test_defaults(self):
        cfg = ChEMBLConfig(input_path="data/in.csv")
        assert cfg.chembl_id_col == "ChEMBL ID"
        assert cfg.keep_extra_columns is False

    def test_custom_chembl_id_col(self):
        cfg = ChEMBLConfig(
            input_path="data/in.csv",
            chembl_id_col="ID",
            keep_extra_columns=True,
        )
        assert cfg.chembl_id_col == "ID"
        assert cfg.keep_extra_columns is True

    def test_frozen(self):
        cfg = ChEMBLConfig(input_path="data/in.csv")
        with pytest.raises(Exception):
            cfg.input_path = "other.csv"

    def test_empty_input_path_raises(self):
        with pytest.raises(ValueError, match="input_path"):
            ChEMBLConfig(input_path="")

    def test_input_path_traversal_raises(self):
        with pytest.raises(ValueError, match="traversal"):
            ChEMBLConfig(input_path="../../etc/passwd")

    def test_empty_chembl_id_col_raises(self):
        with pytest.raises(ValueError, match="chembl_id_col"):
            ChEMBLConfig(input_path="data/in.csv", chembl_id_col="")

    def test_whitespace_chembl_id_col_raises(self):
        with pytest.raises(ValueError, match="chembl_id_col"):
            ChEMBLConfig(input_path="data/in.csv", chembl_id_col="   ")

    def test_keep_extra_columns_must_be_bool(self):
        with pytest.raises(ValueError, match="keep_extra_columns"):
            ChEMBLConfig(input_path="data/in.csv", keep_extra_columns=1)


class TestSMILESConfig:
    """Tests for SMILESConfig dataclass."""

    def test_minimal_creation(self):
        cfg = SMILESConfig(input_path="data/in.csv", smiles_col="SMILES")
        assert cfg.input_path == "data/in.csv"
        assert cfg.smiles_col == "SMILES"

    def test_defaults(self):
        cfg = SMILESConfig(input_path="data/in.csv", smiles_col="SMILES")
        assert cfg.keep_extra_columns is False

    def test_custom_smiles_col(self):
        cfg = SMILESConfig(
            input_path="data/in.csv",
            smiles_col="canonical_smiles",
            keep_extra_columns=True,
        )
        assert cfg.smiles_col == "canonical_smiles"
        assert cfg.keep_extra_columns is True

    def test_frozen(self):
        cfg = SMILESConfig(input_path="data/in.csv", smiles_col="SMILES")
        with pytest.raises(Exception):
            cfg.input_path = "other.csv"

    def test_empty_input_path_raises(self):
        with pytest.raises(ValueError, match="input_path"):
            SMILESConfig(input_path="", smiles_col="SMILES")

    def test_input_path_traversal_raises(self):
        with pytest.raises(ValueError, match="traversal"):
            SMILESConfig(input_path="../../etc/passwd", smiles_col="SMILES")

    def test_empty_smiles_col_raises(self):
        with pytest.raises(ValueError, match="smiles_col"):
            SMILESConfig(input_path="data/in.csv", smiles_col="")

    def test_whitespace_smiles_col_raises(self):
        with pytest.raises(ValueError, match="smiles_col"):
            SMILESConfig(input_path="data/in.csv", smiles_col="   ")

    def test_keep_extra_columns_must_be_bool(self):
        with pytest.raises(ValueError, match="keep_extra_columns"):
            SMILESConfig(input_path="data/in.csv", smiles_col="SMILES", keep_extra_columns=None)
