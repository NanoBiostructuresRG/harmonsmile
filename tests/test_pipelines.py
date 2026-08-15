# SPDX-License-Identifier: LGPL-3.0-or-later
"""Unit tests for harmonsmile.pipelines."""

import logging
import os
import tempfile
from unittest.mock import MagicMock

import pandas as pd
import pytest

from harmonsmile import (
    ChEMBLConfig,
    HarmonizationResult,
    PubChemConfig,
    SMILESConfig,
)
from harmonsmile.pipelines import ChEMBLIngest, PubChemIngest, SMILESPrep


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
    std = MagicMock(spec=["to_iso_kek", "to_lab_harmonized"])
    std.to_iso_kek = lambda smiles: f"rdkit:{smiles}" if pd.notna(smiles) else None
    std.to_lab_harmonized = lambda smiles: (
        HarmonizationResult(f"harmonized:{smiles}", "ok", None, None)
        if pd.notna(smiles) and smiles == "CCO"
        else HarmonizationResult(None, "failed", "invalid SMILES", None)
    )
    return std


class _StaticClient:
    def __init__(self, props: dict):
        self.props = props

    def fetch_props(self, *_args):
        return self.props


class TestPubChemIngest:
    """PubChemIngest output contract tests."""

    def test_empty_input_raises(self):
        path = _empty_csv(["id", "PubChem_CID"])
        cfg = PubChemConfig(input_path=path)
        mock_client = MagicMock()
        try:
            with pytest.raises(ValueError, match="zero rows"):
                PubChemIngest(cfg, client=mock_client).run()
            mock_client.fetch_props.assert_not_called()
        finally:
            os.unlink(path)

    def test_missing_smiles_column_emits_warning(self, caplog):
        path = _write_csv("id,PubChem_CID\n1,702\n")
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
        path = _write_csv("id,PubChem_CID\n1,702\n")
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
        path = _write_csv("id,PubChem_CID,source_note\n1,702,keep me only if asked\n")
        mock_client = _StaticClient({
            "SMILES": "CCO",
            "ConnectivitySMILES": "CCO",
            "MolecularFormula": "C2H6O",
            "MolecularWeight": "46.07",
            "InChI": "InChI=1S/C2H6O/c1-2-3/h3H,2H2,1H3",
            "InChIKey": "LFQSCWFLJHTTHZ-UHFFFAOYSA-N",
            "XLogP": "-0.1",
            "TPSA": "20.2",
            "Charge": "0",
            "HBondDonorCount": "1",
            "HBondAcceptorCount": "1",
            "RotatableBondCount": "0",
            "HeavyAtomCount": "3",
        })
        try:
            out = PubChemIngest(
                PubChemConfig(input_path=path),
                client=mock_client,
                std=_std(),
            ).run()
            assert list(out.columns) == [
                "id", "PubChem_CID", "InChI", "InChIKey",
                "SMILES", "ConnectivitySMILES",
                "SMILES_RDKit",
                "SMILES_Harmonized", "SMILES_Harmonization_Status",
                "SMILES_Harmonization_Message",
                "MolecularFormula", "MW", "XLogP", "TPSA", "Charge",
                "HBondDonorCount", "HBondAcceptorCount",
                "RotatableBondCount", "HeavyAtomCount",
            ]
            assert "SMILES_Harmonization_Error" not in out.columns
            assert out.loc[0, "SMILES_RDKit"] == "rdkit:CCO"
            assert out.loc[0, "ConnectivitySMILES"] == "CCO"
            assert out.loc[0, "SMILES_Harmonized"] == "harmonized:CCO"
            assert out.loc[0, "SMILES_Harmonization_Status"] == "ok"
            assert pd.isna(out.loc[0, "SMILES_Harmonization_Message"])
            assert out.loc[0, "MolecularFormula"] == "C2H6O"
            assert out.loc[0, "InChIKey"] == "LFQSCWFLJHTTHZ-UHFFFAOYSA-N"
            assert out.loc[0, "HeavyAtomCount"] == "3"
            assert out.loc[0, "MW"] == pytest.approx(46.07)
        finally:
            os.unlink(path)

    def test_keep_extra_columns_preserves_metadata_but_not_index_artifacts(self):
        path = _write_csv("Unnamed: 0,id,PubChem_CID,source_note\n0,1,702,metadata\n")
        mock_client = _StaticClient({"SMILES": "CCO"})
        try:
            out = PubChemIngest(
                PubChemConfig(input_path=path, keep_extra_columns=True),
                client=mock_client,
                std=_std(),
            ).run()
            assert "source_note" in out.columns
            assert out.columns[-1] == "source_note"
            assert "Unnamed: 0" not in out.columns
        finally:
            os.unlink(path)

    @pytest.mark.parametrize(
        "column",
        ["PubChem CID", "PubChem_CID", "PubChemCID", "CID"],
    )
    def test_pubchem_cid_input_aliases_are_accepted(self, column):
        path = _write_csv(f"id,{column}\n1,702\n")
        mock_client = _StaticClient({"SMILES": "CCO"})
        try:
            out = PubChemIngest(
                PubChemConfig(input_path=path),
                client=mock_client,
                std=_std(),
            ).run()
            assert "PubChem_CID" in out.columns
            assert "PubChem CID" not in out.columns
            assert out.loc[0, "PubChem_CID"] == "702"
        finally:
            os.unlink(path)

    def test_requested_cid_column_uses_exact_match_first(self):
        path = _write_csv("id,CID,source\n1,702,999\n")
        mock_client = _StaticClient({"SMILES": "CCO"})
        try:
            out = PubChemIngest(
                PubChemConfig(input_path=path, cid_col="CID"),
                client=mock_client,
                std=_std(),
            ).run()
            assert out.loc[0, "PubChem_CID"] == "702"
        finally:
            os.unlink(path)

    def test_requested_cid_column_uses_normalized_alias_match(self):
        path = _write_csv("id,PubChem_CID\n1,702\n")
        mock_client = _StaticClient({"SMILES": "CCO"})
        try:
            out = PubChemIngest(
                PubChemConfig(input_path=path, cid_col="pubchem cid"),
                client=mock_client,
                std=_std(),
            ).run()
            assert out.loc[0, "PubChem_CID"] == "702"
        finally:
            os.unlink(path)

    def test_requested_cid_column_uses_normalized_non_alias_match(self):
        path = _write_csv("id,My CID\n1,702\n")
        mock_client = _StaticClient({"SMILES": "CCO"})
        try:
            out = PubChemIngest(
                PubChemConfig(input_path=path, cid_col="my-cid"),
                client=mock_client,
                std=_std(),
            ).run()
            assert out.loc[0, "PubChem_CID"] == "702"
        finally:
            os.unlink(path)

    def test_ambiguous_alias_columns_fail_clearly(self):
        path = _write_csv("id,PubChem_CID,CID\n1,702,703\n")
        try:
            with pytest.raises(ValueError, match="Ambiguous PubChem CID columns"):
                PubChemIngest(PubChemConfig(input_path=path)).run()
        finally:
            os.unlink(path)

    def test_requested_ambiguous_normalized_column_fails_clearly(self):
        path = _write_csv("id,My CID,my_cid\n1,702,703\n")
        try:
            with pytest.raises(ValueError, match="ambiguous after normalization"):
                PubChemIngest(
                    PubChemConfig(input_path=path, cid_col="my-cid")
                ).run()
        finally:
            os.unlink(path)

    def test_missing_cid_column_fails_with_available_columns(self):
        path = _write_csv("id,source\n1,702\n")
        try:
            with pytest.raises(ValueError, match=r"Available columns: \['id', 'source'\]"):
                PubChemIngest(PubChemConfig(input_path=path)).run()
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
            assert list(out.columns) == [
                "id", "ChEMBL ID", "name", "SMILES", "SMILES_RDKit",
                "SMILES_Harmonized", "SMILES_Harmonization_Status",
                "SMILES_Harmonization_Message", "MW",
            ]
            assert "SMILES_Harmonization_Error" not in out.columns
            assert out.loc[0, "SMILES_RDKit"] == "rdkit:CCO"
            assert out.loc[0, "SMILES_Harmonized"] == "harmonized:CCO"
            assert out.loc[0, "SMILES_Harmonization_Status"] == "ok"
            assert pd.isna(out.loc[0, "SMILES_Harmonization_Message"])
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
            assert list(out.columns) == [
                "id", "SMILES", "SMILES_RDKit", "SMILES_Harmonized",
                "SMILES_Harmonization_Status", "SMILES_Harmonization_Message",
            ]
            assert "SMILES_Harmonization_Error" not in out.columns
            assert out.loc[0, "SMILES_RDKit"] == "rdkit:CCO"
            assert out.loc[0, "SMILES_Harmonized"] == "harmonized:CCO"
            assert out.loc[0, "SMILES_Harmonization_Status"] == "ok"
            assert pd.isna(out.loc[0, "SMILES_Harmonization_Message"])
            assert "source_note" not in out.columns
            assert not os.path.exists(out_path)
        finally:
            os.unlink(path)

    def test_rdkit_kekule_and_harmonized_aromatic_outputs(self):
        path = _write_csv("id,SMILES\n1,c1ccccc1\n")
        try:
            out = SMILESPrep(SMILESConfig(input_path=path, smiles_col="SMILES")).run()
            assert out.loc[0, "SMILES_RDKit"] == "C1=CC=CC=C1"
            assert out.loc[0, "SMILES_Harmonized"] == "c1ccccc1"
        finally:
            os.unlink(path)

    def test_invalid_smiles_row_is_retained_with_harmonization_status(self):
        path = _write_csv("id,SMILES\n1,invalid\n")
        try:
            out = SMILESPrep(
                SMILESConfig(input_path=path, smiles_col="SMILES"),
                std=_std(),
            ).run()
            assert len(out) == 1
            assert pd.isna(out.loc[0, "SMILES_Harmonized"])
            assert out.loc[0, "SMILES_Harmonization_Status"] != "ok"
            assert out.loc[0, "SMILES_Harmonization_Message"] == "invalid SMILES"
        finally:
            os.unlink(path)

    def test_simple_salt_row_gets_harmonized_parent_with_warning(self):
        path = _write_csv("id,SMILES\n1,[Na+].CCO\n")
        try:
            out = SMILESPrep(SMILESConfig(input_path=path, smiles_col="SMILES")).run()
            assert len(out) == 1
            assert out.loc[0, "SMILES_Harmonized"] == "CCO"
            assert out.loc[0, "SMILES_Harmonization_Status"] == "ok_with_warnings"
            assert out.loc[0, "SMILES_Harmonization_Message"] == (
                "salt/counterion removed during controlled parent standardization"
            )
        finally:
            os.unlink(path)

    def test_ambiguous_multicomponent_row_is_not_silently_ok(self):
        path = _write_csv("id,SMILES\n1,CCO.CCN\n")
        try:
            out = SMILESPrep(SMILESConfig(input_path=path, smiles_col="SMILES")).run()
            assert len(out) == 1
            assert pd.isna(out.loc[0, "SMILES_Harmonized"])
            assert out.loc[0, "SMILES_Harmonization_Status"] == "unsupported"
            assert "ambiguous" in out.loc[0, "SMILES_Harmonization_Message"]
        finally:
            os.unlink(path)

    def test_keep_extra_columns_preserves_metadata_but_not_index_artifacts(self):
        path = _write_csv("Unnamed: 0,id,SMILES,source_note\n0,1,CCO,metadata\n")
        try:
            out = SMILESPrep(
                SMILESConfig(input_path=path, smiles_col="SMILES", keep_extra_columns=True),
                std=_std(),
            ).run()
            assert list(out.columns) == [
                "id", "SMILES", "SMILES_RDKit", "SMILES_Harmonized",
                "SMILES_Harmonization_Status", "SMILES_Harmonization_Message",
                "source_note",
            ]
            assert "Unnamed: 0" not in out.columns
        finally:
            os.unlink(path)
