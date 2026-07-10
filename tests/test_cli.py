# SPDX-License-Identifier: LGPL-3.0-or-later
"""Tests for harmonsmile._cli."""

from __future__ import annotations

import os
from unittest.mock import patch

import pandas as pd
import pytest

import harmonsmile._cli as cli
from harmonsmile._cli import _parse, main


def _argv(*args: str) -> list[str]:
    """Return a plain list of strings."""
    return list(args)


class TestParseBatchPubChem:
    def test_pubchem_batch_basic(self):
        args = _parse(_argv("--pubchem-in", "in.csv", "--pubchem-out", "out.csv"))
        assert args.pub_in == "in.csv"
        assert args.pub_out == "out.csv"
        assert args.pubchem_cidcol is None

    def test_pubchem_batch_custom_cidcol(self):
        args = _parse(_argv(
            "--pubchem-in", "in.csv",
            "--pubchem-out", "out.csv",
            "--pubchem-cidcol", "CID",
        ))
        assert args.pubchem_cidcol == "CID"

    def test_pubchem_missing_out_raises(self):
        with pytest.raises(SystemExit):
            _parse(_argv("--pubchem-in", "in.csv"))

    def test_pubchem_missing_in_raises(self):
        with pytest.raises(SystemExit):
            _parse(_argv("--pubchem-out", "out.csv"))


class TestParseBatchChEMBL:
    def test_chembl_batch_basic(self):
        args = _parse(_argv("--chembl-in", "in.csv", "--chembl-out", "out.csv"))
        assert args.chembl_in == "in.csv"
        assert args.chembl_out == "out.csv"
        assert args.chembl_idcol == "ChEMBL ID"

    def test_chembl_batch_custom_idcol(self):
        args = _parse(_argv(
            "--chembl-in", "in.csv",
            "--chembl-out", "out.csv",
            "--chembl-idcol", "ID",
        ))
        assert args.chembl_idcol == "ID"

    def test_chembl_missing_out_raises(self):
        with pytest.raises(SystemExit):
            _parse(_argv("--chembl-in", "in.csv"))

    def test_chembl_missing_in_raises(self):
        with pytest.raises(SystemExit):
            _parse(_argv("--chembl-out", "out.csv"))


class TestParseBatchSMILES:
    def test_smiles_batch_basic(self):
        args = _parse(_argv(
            "--smiles-in", "in.csv",
            "--smiles-col", "SMILES",
            "--smiles-out", "out.csv",
        ))
        assert args.smiles_in == "in.csv"
        assert args.smiles_col == "SMILES"
        assert args.smiles_out == "out.csv"

    def test_smiles_missing_out_raises(self):
        with pytest.raises(SystemExit):
            _parse(_argv("--smiles-in", "in.csv", "--smiles-col", "SMILES"))

    def test_smiles_missing_in_raises(self):
        with pytest.raises(SystemExit):
            _parse(_argv("--smiles-out", "out.csv", "--smiles-col", "SMILES"))

    def test_smiles_missing_col_raises(self):
        with pytest.raises(SystemExit):
            _parse(_argv("--smiles-in", "in.csv", "--smiles-out", "out.csv"))


class TestParseSingleEntry:
    def test_pubchem_cid(self):
        args = _parse(_argv("--pubchem-cid", "2723949"))
        assert args.pubchem_cid == "2723949"
        assert args.chembl_id is None

    def test_chembl_id(self):
        args = _parse(_argv("--chembl-id", "CHEMBL294199"))
        assert args.chembl_id == "CHEMBL294199"
        assert args.pubchem_cid is None

    def test_pubchem_cid_and_pubchem_in_mutually_exclusive(self):
        with pytest.raises(SystemExit):
            _parse(_argv(
                "--pubchem-cid", "2723949",
                "--pubchem-in", "in.csv",
                "--pubchem-out", "out.csv",
            ))

    def test_chembl_id_and_chembl_in_mutually_exclusive(self):
        with pytest.raises(SystemExit):
            _parse(_argv(
                "--chembl-id", "CHEMBL294199",
                "--chembl-in", "in.csv",
                "--chembl-out", "out.csv",
            ))


@pytest.fixture()
def mock_pipelines():
    """Patch all three pipeline classes inside _cli so no real network occurs."""
    with (
        patch("harmonsmile._cli.PubChemIngest") as MockPubChem,
        patch("harmonsmile._cli.ChEMBLIngest") as MockChEMBL,
        patch("harmonsmile._cli.SMILESPrep") as MockSMILES,
        patch("harmonsmile._cli.save_table") as mock_save,
    ):
        MockPubChem.return_value.run.return_value = pd.DataFrame({"kind": ["pubchem"]})
        MockChEMBL.return_value.run.return_value = pd.DataFrame({"kind": ["chembl"]})
        MockSMILES.return_value.run.return_value = pd.DataFrame({"kind": ["smiles"]})
        yield MockPubChem, MockChEMBL, MockSMILES, mock_save


class TestMainBatchPubChem:
    def test_pubchem_batch_calls_run_then_save_table(self, mock_pipelines):
        MockPubChem, _, _, mock_save = mock_pipelines
        main(_argv("--pubchem-in", "in.csv", "--pubchem-out", "out.csv"))
        MockPubChem.assert_called_once()
        MockPubChem.return_value.run.assert_called_once()
        mock_save.assert_called_once()
        assert mock_save.call_args[0][1] == "out.csv"

    def test_pubchem_batch_config_receives_no_output_path(self, mock_pipelines):
        MockPubChem, _, _, _ = mock_pipelines
        main(_argv("--pubchem-in", "in.csv", "--pubchem-out", "out.csv"))
        cfg_arg = MockPubChem.call_args[0][0]
        assert cfg_arg.input_path == "in.csv"
        assert not hasattr(cfg_arg, "output_path")


class TestMainBatchChEMBL:
    def test_chembl_batch_calls_run_then_save_table(self, mock_pipelines):
        _, MockChEMBL, _, mock_save = mock_pipelines
        main(_argv("--chembl-in", "in.csv", "--chembl-out", "out.csv"))
        MockChEMBL.assert_called_once()
        MockChEMBL.return_value.run.assert_called_once()
        assert mock_save.call_args[0][1] == "out.csv"

    def test_chembl_batch_config_receives_no_output_path(self, mock_pipelines):
        _, MockChEMBL, _, _ = mock_pipelines
        main(_argv("--chembl-in", "in.csv", "--chembl-out", "out.csv"))
        cfg_arg = MockChEMBL.call_args[0][0]
        assert cfg_arg.input_path == "in.csv"
        assert not hasattr(cfg_arg, "output_path")


class TestMainBatchSMILES:
    def test_smiles_batch_calls_run_then_save_table(self, mock_pipelines):
        _, _, MockSMILES, mock_save = mock_pipelines
        main(_argv("--smiles-in", "in.csv", "--smiles-col", "SMILES", "--smiles-out", "out.csv"))
        MockSMILES.assert_called_once()
        MockSMILES.return_value.run.assert_called_once()
        assert mock_save.call_args[0][1] == "out.csv"

    def test_smiles_batch_config_receives_args_without_output_path(self, mock_pipelines):
        _, _, MockSMILES, _ = mock_pipelines
        main(_argv("--smiles-in", "in.csv", "--smiles-col", "SMILES", "--smiles-out", "out.csv"))
        cfg_arg = MockSMILES.call_args[0][0]
        assert cfg_arg.input_path == "in.csv"
        assert cfg_arg.smiles_col == "SMILES"
        assert not hasattr(cfg_arg, "output_path")


class TestMainSingleEntryPubChem:
    def test_pubchem_cid_calls_run_then_saves_default_path(self, mock_pipelines):
        MockPubChem, _, _, mock_save = mock_pipelines
        with patch("harmonsmile._cli.os.unlink"):
            main(_argv("--pubchem-cid", "2723949"))
        MockPubChem.assert_called_once()
        MockPubChem.return_value.run.assert_called_once()
        assert mock_save.call_args[0][1] == os.path.join("results", "CID2723949_harmonsmile.csv")

    def test_pubchem_cid_temp_file_deleted(self, mock_pipelines):
        with patch("harmonsmile._cli.os.unlink") as mock_unlink:
            main(_argv("--pubchem-cid", "2723949"))
        mock_unlink.assert_called_once()
        assert mock_unlink.call_args[0][0].endswith(".csv")

    def test_pubchem_cid_temp_file_contains_correct_cid(self, mock_pipelines):
        MockPubChem, _, _, _ = mock_pipelines
        captured_df: list[pd.DataFrame] = []

        def capture_on_run():
            cfg = MockPubChem.call_args[0][0]
            captured_df.append(pd.read_csv(cfg.input_path))
            return pd.DataFrame()

        MockPubChem.return_value.run.side_effect = capture_on_run

        with patch("harmonsmile._cli.os.unlink"):
            main(_argv("--pubchem-cid", "2723949"))

        df = captured_df[0]
        assert "PubChem_CID" in df.columns
        assert str(df["PubChem_CID"].iloc[0]) == "2723949"


class TestMainSingleEntryChEMBL:
    def test_chembl_id_calls_run_then_saves_default_path(self, mock_pipelines):
        _, MockChEMBL, _, mock_save = mock_pipelines
        with patch("harmonsmile._cli.os.unlink"):
            main(_argv("--chembl-id", "CHEMBL294199"))
        MockChEMBL.assert_called_once()
        MockChEMBL.return_value.run.assert_called_once()
        assert mock_save.call_args[0][1] == os.path.join("results", "CHEMBL294199_harmonsmile.csv")

    def test_chembl_id_temp_file_deleted(self, mock_pipelines):
        with patch("harmonsmile._cli.os.unlink") as mock_unlink:
            main(_argv("--chembl-id", "CHEMBL294199"))
        mock_unlink.assert_called_once()
        assert mock_unlink.call_args[0][0].endswith(".csv")

    def test_chembl_id_temp_file_contains_correct_id(self, mock_pipelines):
        _, MockChEMBL, _, _ = mock_pipelines
        captured_df: list[pd.DataFrame] = []

        def capture_on_run():
            cfg = MockChEMBL.call_args[0][0]
            captured_df.append(pd.read_csv(cfg.input_path))
            return pd.DataFrame()

        MockChEMBL.return_value.run.side_effect = capture_on_run

        with patch("harmonsmile._cli.os.unlink"):
            main(_argv("--chembl-id", "CHEMBL294199"))

        df = captured_df[0]
        assert "ChEMBL ID" in df.columns
        assert df["ChEMBL ID"].iloc[0] == "CHEMBL294199"


class TestMainOutputDirs:
    def test_ensure_dirs_removed(self):
        assert not hasattr(cli, "_ensure_dirs")

    def test_save_cli_output_removed(self):
        assert not hasattr(cli, "_save_cli_output")

    def test_unsafe_output_path_rejected_without_creating_parent(self, tmp_path):
        blocked_parent = tmp_path / "blocked"
        unsafe_output = blocked_parent / ".." / "outside.csv"
        with (
            patch("harmonsmile._cli.SMILESPrep") as MockSMILES,
            pytest.raises(ValueError, match="traversal"),
        ):
            MockSMILES.return_value.run.return_value = pd.DataFrame({"SMILES": ["CCO"]})
            main(_argv(
                "--smiles-in", "in.csv",
                "--smiles-col", "SMILES",
                "--smiles-out", os.fspath(unsafe_output),
            ))
        assert not blocked_parent.exists()
        assert not (tmp_path / "outside.csv").exists()


class TestMainNoArgs:
    def test_no_args_raises_system_exit(self):
        with pytest.raises(SystemExit) as exc_info:
            main(_argv())
        assert exc_info.value.code != 0 or isinstance(exc_info.value.code, str)

    def test_no_args_message_mentions_flags(self, capsys):
        with pytest.raises(SystemExit) as exc_info:
            main(_argv())
        assert "--pubchem-in" in str(exc_info.value)
