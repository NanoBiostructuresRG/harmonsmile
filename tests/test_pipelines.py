# SPDX-License-Identifier: LGPL-3.0-or-later
"""Unit tests for harmonsmile.pipelines."""

import logging
import os
import tempfile

import pandas as pd
import pytest
from unittest.mock import MagicMock

from harmonsmile import PubChemConfig, ChEMBLConfig, SMILESConfig
from harmonsmile.pipelines import PubChemIngest, ChEMBLIngest, SMILESPrep


def _write_csv(content: str) -> str:
    """Write content to a temporary CSV file and return its path."""
    f = tempfile.NamedTemporaryFile(mode="w", suffix=".csv",
                                    delete=False, encoding="utf-8")
    f.write(content)
    f.close()
    return f.name


def _empty_csv(columns: list[str]) -> str:
    """Write a header-only CSV (zero rows) and return its path."""
    return _write_csv(",".join(columns) + "\n")


def _std() -> MagicMock:
    std = MagicMock(spec=["to_iso_kek"])
    std.to_iso_kek = lambda smiles: f"rdkit:{smiles}" if pd.notna(smiles) else None
    return std


class _StaticClient:
    def __init__(self, props: dict):
        self.props = props

    def fetch_props(self, *_args):
        return self.props


class TestPubChemIngest:
    """PubChemIngest output contract tests."""

    def test_empty_input_raises(self):
        path = _empty_csv(["id", "PubChem CID"])
        cfg = PubChemConfig(input_path=path)
        mock_client = MagicMock()
        try:
            with pytest.raises(ValueError, match="zero rows"):
                PubChemIngest(cfg, client=mock_client).run()
            mock_client.fetch_props.assert_not_called()
        finally:
            os.unlink(path)

    def test_missing_smiles_column_emits_warning(self, caplog):
        path = _write_csv("id,PubChem CID\n1,702\n")
        cfg = PubChemConfig(input_path=path, props=("MolecularWeight",))
        mock_client = _StaticClient({"MolecularWeight": "46.07"})

        try:
            with caplog.at_level(logging.WARNING, logger="harmonsmile.pipelines"):
                out = PubChemIngest(cfg, client=mock_client, std=_std()).run()
            assert isinstance(out, pd.DataFrame)
            assert any("SMILES" in msg for msg in caplog.messages)
        finally:
            os.unlink(path)

    def test_run_returns_dataframe_and_does_not_create_output(self):
        path = _write_csv("id,PubChem CID\n1,702\n")
        out_path = path.replace(".csv", "_out.csv")
        mock_client = _StaticClient({
            "SMILES": "CCO",
            "MolecularWeight": "46.07",
        })
        try:
            out = PubChemIngest(
                PubChemConfig(input_path=path),
                client=mock_client,
                std=_std(),
            ).run()
            assert isinstance(out, pd.DataFrame)
            assert not os.path.exists(out_path)
        finally:
            os.unlink(path)

    def test_strict_schema_by_default(self):
        path = _write_csv("id,PubChem CID,source_note\n1,702,keep me only if asked\n")
        mock_client = _StaticClient({
            "SMILES": "CCO",
            "ConnectivitySMILES": "CCO",
            "MolecularWeight": "46.07",
        })
        try:
            out = PubChemIngest(
                PubChemConfig(input_path=path),
                client=mock_client,
                std=_std(),
            ).run()
            assert list(out.columns) == [
                "id", "PubChem CID", "SMILES", "SMILES_RDKit",
                "ConnectivitySMILES", "MW",
            ]
        finally:
            os.unlink(path)

    def test_keep_extra_columns_preserves_metadata_but_not_index_artifacts(self):
        path = _write_csv("Unnamed: 0,id,PubChem CID,source_note\n0,1,702,metadata\n")
        mock_client = _StaticClient({"SMILES": "CCO"})
        try:
            out = PubChemIngest(
                PubChemConfig(input_path=path, keep_extra_columns=True),
                client=mock_client,
                std=_std(),
            ).run()
            assert "source_note" in out.columns
            assert "Unnamed: 0" not in out.columns
        finally:
            os.unlink(path)


class TestChEMBLIngest:
    """ChEMBLIngest output contract tests."""

    def test_empty_input_raises(self):
        path = _empty_csv(["id", "ChEMBL ID"])
        cfg = ChEMBLConfig(input_path=path)
        mock_client = MagicMock()
        try:
            with pytest.raises(ValueError, match="zero rows"):
                ChEMBLIngest(cfg, client=mock_client).run()
            mock_client.fetch_props.assert_not_called()
        finally:
            os.unlink(path)

    def test_strict_schema_and_no_file_write(self):
        path = _write_csv("id,ChEMBL ID,source_note\n1,CHEMBL1,metadata\n")
        out_path = path.replace(".csv", "_out.csv")
        mock_client = _StaticClient({
            "pref_name": "Ethanol",
            "canonical_smiles": "CCO",
            "full_mwt": "46.07",
        })
        try:
            out = ChEMBLIngest(
                ChEMBLConfig(input_path=path),
                client=mock_client,
                std=_std(),
            ).run()
            assert list(out.columns) == ["id", "ChEMBL ID", "name", "SMILES", "SMILES_RDKit", "MW"]
            assert not os.path.exists(out_path)
        finally:
            os.unlink(path)

    def test_keep_extra_columns_preserves_metadata_but_not_index_artifacts(self):
        path = _write_csv("Unnamed_0,id,ChEMBL ID,source_note\n0,1,CHEMBL1,metadata\n")
        mock_client = _StaticClient({"canonical_smiles": "CCO"})
        try:
            out = ChEMBLIngest(
                ChEMBLConfig(input_path=path, keep_extra_columns=True),
                client=mock_client,
                std=_std(),
            ).run()
            assert "source_note" in out.columns
            assert "Unnamed_0" not in out.columns
        finally:
            os.unlink(path)


class TestSMILESPrep:
    """SMILESPrep output contract tests."""

    def test_empty_input_raises(self):
        path = _empty_csv(["id", "SMILES"])
        cfg = SMILESConfig(input_path=path, smiles_col="SMILES")
        mock_std = MagicMock()
        try:
            with pytest.raises(ValueError, match="zero rows"):
                SMILESPrep(cfg, std=mock_std).run()
            mock_std.to_iso_kek.assert_not_called()
        finally:
            os.unlink(path)

    def test_empty_input_does_not_create_output_dir(self):
        path = _empty_csv(["id", "SMILES"])
        with tempfile.TemporaryDirectory() as tmpdir:
            out = os.path.join(tmpdir, "new_subdir", "out.csv")
            cfg = SMILESConfig(input_path=path, smiles_col="SMILES")
            try:
                with pytest.raises(ValueError):
                    SMILESPrep(cfg).run()
                assert not os.path.exists(os.path.dirname(out))
            finally:
                os.unlink(path)

    def test_strict_schema_by_default_and_no_file_write(self):
        path = _write_csv("id,SMILES,source_note\n1,CCO,metadata\n")
        out_path = path.replace(".csv", "_out.csv")
        try:
            out = SMILESPrep(SMILESConfig(input_path=path, smiles_col="SMILES"), std=_std()).run()
            assert isinstance(out, pd.DataFrame)
            assert list(out.columns) == ["id", "SMILES", "SMILES_RDKit"]
            assert "source_note" not in out.columns
            assert not os.path.exists(out_path)
        finally:
            os.unlink(path)

    def test_keep_extra_columns_preserves_metadata_but_not_index_artifacts(self):
        path = _write_csv("Unnamed: 0,id,SMILES,source_note\n0,1,CCO,metadata\n")
        try:
            out = SMILESPrep(
                SMILESConfig(input_path=path, smiles_col="SMILES", keep_extra_columns=True),
                std=_std(),
            ).run()
            assert list(out.columns) == ["id", "SMILES", "SMILES_RDKit", "source_note"]
            assert "Unnamed: 0" not in out.columns
        finally:
            os.unlink(path)
