# SPDX-License-Identifier: LGPL-3.0-or-later
"""Unit tests for harmonsmile.io."""

import os
import tempfile
import pytest
import pandas as pd
from harmonsmile.io import sanitize_cid, load_table, save_table


class TestSanitizeCid:
    """Tests for sanitize_cid."""

    def test_float_cid(self):
        """Float CID is converted to integer string."""
        assert sanitize_cid(2723949.0) == "2723949"

    def test_string_cid(self):
        """String CID with whitespace is cleaned."""
        assert sanitize_cid("  12345  ") == "12345"

    def test_int_cid(self):
        """Integer CID is converted to string."""
        assert sanitize_cid(12345) == "12345"

    def test_none_returns_none(self):
        """None returns None."""
        assert sanitize_cid(None) is None

    def test_nan_returns_none(self):
        """NaN returns None."""
        assert sanitize_cid(float("nan")) is None

    def test_non_numeric_string_returns_none(self):
        """Non-numeric string returns None."""
        assert sanitize_cid("abc") is None

    def test_mixed_string_extracts_digits(self):
        """String with mixed characters extracts only digits."""
        assert sanitize_cid("CID12345") == "12345"


class TestLoadTable:
    """Tests for load_table."""

    def test_load_csv(self):
        """CSV file is loaded correctly."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv",
                                         delete=False, encoding="utf-8") as f:
            f.write("id,SMILES\n1,c1ccccc1\n2,CCO\n")
            path = f.name
        try:
            df = load_table(path)
            assert len(df) == 2
            assert "SMILES" in df.columns
        finally:
            os.unlink(path)

    def test_load_tsv(self):
        """TSV file is loaded correctly."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".tsv",
                                         delete=False, encoding="utf-8") as f:
            f.write("id\tSMILES\n1\tc1ccccc1\n")
            path = f.name
        try:
            df = load_table(path)
            assert len(df) == 1
        finally:
            os.unlink(path)

    def test_unsupported_format_raises(self):
        """Unsupported file format raises ValueError."""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            f.write(b"{}")
            path = f.name
        try:
            with pytest.raises(ValueError, match="Unsupported format"):
                load_table(path)
        finally:
            os.unlink(path)

    def test_id_column_cleaned(self):
        """id column is converted to Int64."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv",
                                         delete=False, encoding="utf-8") as f:
            f.write("id,SMILES\n1,CCO\n2,c1ccccc1\n")
            path = f.name
        try:
            df = load_table(path)
            assert df["id"].dtype.name == "Int64"
        finally:
            os.unlink(path)

    def test_pubchem_cid_column_sanitized(self):
        """PubChem CID column is sanitized."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv",
                                         delete=False, encoding="utf-8") as f:
            f.write("id,PubChem CID\n1,2723949.0\n")
            path = f.name
        try:
            df = load_table(path)
            assert df["PubChem CID"].iloc[0] == "2723949"
        finally:
            os.unlink(path)


class TestSaveTable:
    """Tests for save_table."""

    def test_saves_csv(self):
        """DataFrame is saved as CSV."""
        df = pd.DataFrame({"SMILES": ["CCO"], "SMILES_RDKit": ["CCO"]})
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
            path = f.name
        try:
            save_table(df, path)
            assert os.path.exists(path)
        finally:
            os.unlink(path)

    def test_creates_parent_dirs(self):
        """Parent directories are created if they do not exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            out = os.path.join(tmpdir, "nested", "dir", "out.csv")
            df = pd.DataFrame({"a": [1]})
            save_table(df, out)
            assert os.path.exists(out)

    def test_roundtrip(self):
        """Data survives a save/load roundtrip."""
        df = pd.DataFrame({"SMILES": ["CCO", "c1ccccc1"]})
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
            path = f.name
        try:
            save_table(df, path)
            df2 = pd.read_csv(path)
            assert list(df2["SMILES"]) == ["CCO", "c1ccccc1"]
        finally:
            os.unlink(path)
