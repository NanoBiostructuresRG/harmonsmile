# SPDX-License-Identifier: LGPL-3.0-or-later
"""Unit tests for harmonsmile.pipelines — introduced in v0.1.3."""

import logging
import os
import tempfile

import pandas as pd
import pytest
from unittest.mock import MagicMock, patch

from harmonsmile import Config
from harmonsmile.pipelines import PubChemIngest, ChEMBLIngest, SMILESPrep


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# PubChemIngest
# ---------------------------------------------------------------------------

class TestPubChemIngestEmptyDataFrame:
    """PubChemIngest.run() raises ValueError on empty input."""

    def test_empty_input_raises(self):
        """Zero-row input file raises ValueError before any API call."""
        path = _empty_csv(["id", "PubChem CID"])
        out = path.replace(".csv", "_out.csv")
        cfg = Config(input_path=path, output_path=out)
        mock_client = MagicMock()
        try:
            with pytest.raises(ValueError, match="zero rows"):
                PubChemIngest(cfg, client=mock_client).run()
            mock_client.fetch_props.assert_not_called()
        finally:
            os.unlink(path)


class TestPubChemIngestMissingSmiles:
    """PubChemIngest.run() emits a warning when SMILES column is absent."""

    def test_missing_smiles_column_emits_warning(self, caplog):
        """If SMILES is not in fetched properties, a logger.warning is emitted."""
        path = _write_csv("id,PubChem CID\n1,702\n")
        out = path.replace(".csv", "_out.csv")
        cfg = Config(
            input_path=path,
            output_path=out,
            props=("MolecularWeight",),   # SMILES intentionally excluded
        )
        mock_client = MagicMock()
        mock_client.fetch_props.return_value = {"MolecularWeight": "46.07"}
        mock_std = MagicMock()

        try:
            with caplog.at_level(logging.WARNING, logger="harmonsmile.pipelines"):
                PubChemIngest(cfg, client=mock_client, std=mock_std).run()
            assert any("SMILES" in msg for msg in caplog.messages), (
                "Expected a warning mentioning 'SMILES' but got: " + str(caplog.messages)
            )
        finally:
            os.unlink(path)
            if os.path.exists(out):
                os.unlink(out)


# ---------------------------------------------------------------------------
# ChEMBLIngest
# ---------------------------------------------------------------------------

class TestChEMBLIngestEmptyDataFrame:
    """ChEMBLIngest.run() raises ValueError on empty input."""

    def test_empty_input_raises(self):
        """Zero-row input file raises ValueError before any API call."""
        path = _empty_csv(["id", "ChEMBL ID"])
        out = path.replace(".csv", "_out.csv")
        mock_client = MagicMock()
        try:
            with pytest.raises(ValueError, match="zero rows"):
                ChEMBLIngest(
                    input_path=path,
                    output_path=out,
                    client=mock_client,
                ).run()
            mock_client.fetch_props.assert_not_called()
        finally:
            os.unlink(path)


# ---------------------------------------------------------------------------
# SMILESPrep
# ---------------------------------------------------------------------------

class TestSMILESPrepEmptyDataFrame:
    """SMILESPrep.run() raises ValueError on empty input."""

    def test_empty_input_raises(self):
        """Zero-row input file raises ValueError before processing."""
        path = _empty_csv(["id", "SMILES"])
        out = path.replace(".csv", "_out.csv")
        mock_std = MagicMock()
        try:
            with pytest.raises(ValueError, match="zero rows"):
                SMILESPrep(
                    input_path=path,
                    smiles_col="SMILES",
                    output_path=out,
                    std=mock_std,
                ).run()
            mock_std.to_iso_kek.assert_not_called()
        finally:
            os.unlink(path)

    def test_empty_input_does_not_create_output_dir(self):
        """Empty input must not create output directories."""
        path = _empty_csv(["id", "SMILES"])
        with tempfile.TemporaryDirectory() as tmpdir:
            out = os.path.join(tmpdir, "new_subdir", "out.csv")
            try:
                with pytest.raises(ValueError):
                    SMILESPrep(
                        input_path=path,
                        smiles_col="SMILES",
                        output_path=out,
                    ).run()
                assert not os.path.exists(os.path.dirname(out)), (
                    "Output directory must not be created when input is empty."
                )
            finally:
                os.unlink(path)
