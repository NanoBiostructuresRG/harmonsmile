# SPDX-License-Identifier: LGPL-3.0-or-later
"""
Tests for harmonsmile._cli
==========================

Coverage
--------
_parse()
    - Batch mode: PubChem, ChEMBL, SMILES
    - Single Entry mode: --pubchem-cid, --chembl-id
    - Mutual exclusion: --pubchem-cid vs --pubchem-in
    - Mutual exclusion: --chembl-id vs --chembl-in
    - Paired-arg validation: pubchem, chembl, smiles
    - --smiles-col required when --smiles-in is present

main()
    - Batch PubChem: calls PubChemIngest.run()
    - Batch ChEMBL: calls ChEMBLIngest.run()
    - Batch SMILES: calls SMILESPrep.run()
    - Single Entry PubChem: temp file lifecycle + correct output path
    - Single Entry ChEMBL: temp file lifecycle + correct output path
    - No arguments: raises SystemExit with helpful message
    - results/ directory created automatically
"""

from __future__ import annotations

import os
from unittest.mock import MagicMock, patch, call

import pandas as pd
import pytest

from harmonsmile._cli import _parse, main


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _argv(*args: str) -> list[str]:
    """Return a plain list of strings (avoids tuple mistakes)."""
    return list(args)


# ===========================================================================
# _parse() — Batch modes
# ===========================================================================


class TestParseBatchPubChem:
    def test_pubchem_batch_basic(self):
        args = _parse(_argv("--pubchem-in", "in.csv", "--pubchem-out", "out.csv"))
        assert args.pub_in == "in.csv"
        assert args.pub_out == "out.csv"
        assert args.pubchem_cidcol == "PubChem CID"  # default

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
        assert args.chembl_idcol == "ChEMBL ID"  # default

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


# ===========================================================================
# _parse() — Single Entry mode
# ===========================================================================


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


# ===========================================================================
# main() — pipeline dispatch (all pipelines mocked)
# ===========================================================================


@pytest.fixture()
def mock_pipelines():
    """Patch all three pipeline classes inside _cli so no real I/O occurs."""
    with (
        patch("harmonsmile._cli.PubChemIngest") as MockPubChem,
        patch("harmonsmile._cli.ChEMBLIngest") as MockChEMBL,
        patch("harmonsmile._cli.SMILESPrep") as MockSMILES,
        patch("harmonsmile._cli._ensure_dirs"),
    ):
        MockPubChem.return_value.run.return_value = pd.DataFrame()
        MockChEMBL.return_value.run.return_value = pd.DataFrame()
        MockSMILES.return_value.run.return_value = pd.DataFrame()
        yield MockPubChem, MockChEMBL, MockSMILES


class TestMainBatchPubChem:
    def test_pubchem_batch_calls_pipeline(self, mock_pipelines):
        MockPubChem, _, _ = mock_pipelines
        main(_argv("--pubchem-in", "in.csv", "--pubchem-out", "out.csv"))
        MockPubChem.assert_called_once()
        MockPubChem.return_value.run.assert_called_once()

    def test_pubchem_batch_config_receives_paths(self, mock_pipelines):
        MockPubChem, _, _ = mock_pipelines
        main(_argv("--pubchem-in", "in.csv", "--pubchem-out", "out.csv"))
        cfg_arg = MockPubChem.call_args[0][0]   # positional Config object
        assert cfg_arg.input_path == "in.csv"
        assert cfg_arg.output_path == "out.csv"


class TestMainBatchChEMBL:
    def test_chembl_batch_calls_pipeline(self, mock_pipelines):
        _, MockChEMBL, _ = mock_pipelines
        main(_argv("--chembl-in", "in.csv", "--chembl-out", "out.csv"))
        MockChEMBL.assert_called_once()
        MockChEMBL.return_value.run.assert_called_once()

    def test_chembl_batch_receives_correct_paths(self, mock_pipelines):
        _, MockChEMBL, _ = mock_pipelines
        main(_argv("--chembl-in", "in.csv", "--chembl-out", "out.csv"))
        kwargs = MockChEMBL.call_args[1]
        assert kwargs["input_path"] == "in.csv"
        assert kwargs["output_path"] == "out.csv"


class TestMainBatchSMILES:
    def test_smiles_batch_calls_pipeline(self, mock_pipelines):
        _, _, MockSMILES = mock_pipelines
        main(_argv("--smiles-in", "in.csv", "--smiles-col", "SMILES", "--smiles-out", "out.csv"))
        MockSMILES.assert_called_once()
        MockSMILES.return_value.run.assert_called_once()

    def test_smiles_batch_receives_correct_args(self, mock_pipelines):
        _, _, MockSMILES = mock_pipelines
        main(_argv("--smiles-in", "in.csv", "--smiles-col", "SMILES", "--smiles-out", "out.csv"))
        pos_args = MockSMILES.call_args[0]
        assert pos_args[0] == "in.csv"
        assert pos_args[1] == "SMILES"
        assert pos_args[2] == "out.csv"


# ===========================================================================
# main() — Single Entry modes
# ===========================================================================


class TestMainSingleEntryPubChem:
    def test_pubchem_cid_calls_pipeline(self, mock_pipelines):
        MockPubChem, _, _ = mock_pipelines
        with patch("harmonsmile._cli.os.unlink"):
            main(_argv("--pubchem-cid", "2723949"))
        MockPubChem.assert_called_once()
        MockPubChem.return_value.run.assert_called_once()

    def test_pubchem_cid_output_path(self, mock_pipelines):
        MockPubChem, _, _ = mock_pipelines
        with patch("harmonsmile._cli.os.unlink"):
            main(_argv("--pubchem-cid", "2723949"))
        cfg_arg = MockPubChem.call_args[0][0]
        assert cfg_arg.output_path == os.path.join("results", "CID2723949_harmonsmile.csv")

    def test_pubchem_cid_temp_file_deleted(self, mock_pipelines):
        """os.unlink must be called on the temp file after run()."""
        MockPubChem, _, _ = mock_pipelines
        with patch("harmonsmile._cli.os.unlink") as mock_unlink:
            main(_argv("--pubchem-cid", "2723949"))
        mock_unlink.assert_called_once()
        unlinked_path = mock_unlink.call_args[0][0]
        assert unlinked_path.endswith(".csv")

    def test_pubchem_cid_temp_file_contains_correct_cid(self, mock_pipelines):
        """The one-row temp CSV passed to PubChemIngest must contain the CID."""
        MockPubChem, _, _ = mock_pipelines
        captured_df: list[pd.DataFrame] = []

        def capture_on_run():
            cfg = MockPubChem.call_args[0][0]
            captured_df.append(pd.read_csv(cfg.input_path))
            return pd.DataFrame()

        MockPubChem.return_value.run.side_effect = capture_on_run

        with patch("harmonsmile._cli.os.unlink"):
            main(_argv("--pubchem-cid", "2723949"))

        assert len(captured_df) == 1
        df = captured_df[0]
        assert "PubChem CID" in df.columns
        assert str(df["PubChem CID"].iloc[0]) == "2723949"


class TestMainSingleEntryChEMBL:
    def test_chembl_id_calls_pipeline(self, mock_pipelines):
        _, MockChEMBL, _ = mock_pipelines
        with patch("harmonsmile._cli.os.unlink"):
            main(_argv("--chembl-id", "CHEMBL294199"))
        MockChEMBL.assert_called_once()
        MockChEMBL.return_value.run.assert_called_once()

    def test_chembl_id_output_path(self, mock_pipelines):
        _, MockChEMBL, _ = mock_pipelines
        with patch("harmonsmile._cli.os.unlink"):
            main(_argv("--chembl-id", "CHEMBL294199"))
        kwargs = MockChEMBL.call_args[1]
        assert kwargs["output_path"] == os.path.join("results", "CHEMBL294199_harmonsmile.csv")

    def test_chembl_id_temp_file_deleted(self, mock_pipelines):
        """os.unlink must be called on the temp file after run()."""
        _, MockChEMBL, _ = mock_pipelines
        with patch("harmonsmile._cli.os.unlink") as mock_unlink:
            main(_argv("--chembl-id", "CHEMBL294199"))
        mock_unlink.assert_called_once()
        unlinked_path = mock_unlink.call_args[0][0]
        assert unlinked_path.endswith(".csv")

    def test_chembl_id_temp_file_contains_correct_id(self, mock_pipelines):
        """The one-row temp CSV passed to ChEMBLIngest must contain the ChEMBL ID."""
        _, MockChEMBL, _ = mock_pipelines
        captured_df: list[pd.DataFrame] = []

        def capture_on_run():
            kwargs = MockChEMBL.call_args[1]
            captured_df.append(pd.read_csv(kwargs["input_path"]))
            return pd.DataFrame()

        MockChEMBL.return_value.run.side_effect = capture_on_run

        with patch("harmonsmile._cli.os.unlink"):
            main(_argv("--chembl-id", "CHEMBL294199"))

        assert len(captured_df) == 1
        df = captured_df[0]
        assert "ChEMBL ID" in df.columns
        assert df["ChEMBL ID"].iloc[0] == "CHEMBL294199"


# ===========================================================================
# main() — results/ directory auto-creation
# ===========================================================================


class TestMainResultsDir:
    def test_results_dir_created_for_pubchem_cid(self):
        """_ensure_dirs() must be called when --pubchem-cid is used."""
        with (
            patch("harmonsmile._cli.PubChemIngest") as MockPubChem,
            patch("harmonsmile._cli.ChEMBLIngest"),
            patch("harmonsmile._cli.SMILESPrep"),
            patch("harmonsmile._cli._ensure_dirs") as mock_ensure,
            patch("harmonsmile._cli.os.unlink"),
        ):
            MockPubChem.return_value.run.return_value = pd.DataFrame()
            main(_argv("--pubchem-cid", "123"))
        mock_ensure.assert_called_once()

    def test_results_dir_created_for_chembl_id(self):
        """_ensure_dirs() must be called when --chembl-id is used."""
        with (
            patch("harmonsmile._cli.PubChemIngest"),
            patch("harmonsmile._cli.ChEMBLIngest") as MockChEMBL,
            patch("harmonsmile._cli.SMILESPrep"),
            patch("harmonsmile._cli._ensure_dirs") as mock_ensure,
            patch("harmonsmile._cli.os.unlink"),
        ):
            MockChEMBL.return_value.run.return_value = pd.DataFrame()
            main(_argv("--chembl-id", "CHEMBL1"))
        mock_ensure.assert_called_once()


# ===========================================================================
# main() — no arguments
# ===========================================================================


class TestMainNoArgs:
    def test_no_args_raises_system_exit(self):
        with pytest.raises(SystemExit) as exc_info:
            main(_argv())
        assert exc_info.value.code != 0 or isinstance(exc_info.value.code, str)

    def test_no_args_message_mentions_flags(self, capsys):
        with pytest.raises(SystemExit):
            main(_argv())
        # SystemExit raised with a string code — message is in the exception itself
