# SPDX-License-Identifier: LGPL-3.0-or-later
"""Unit tests for harmonsmile.io."""

import os
import tempfile
import pytest
import pandas as pd
from harmonsmile.io import _sanitize_cid, load_table, save_table


class TestSanitizeCid:
    """Tests for _sanitize_cid."""

    def test_float_cid(self):
        """Float CID is converted to integer string."""
        assert _sanitize_cid(2723949.0) == "2723949"

    def test_string_cid(self):
        """String CID with whitespace is cleaned."""
        assert _sanitize_cid("  12345  ") == "12345"

    def test_int_cid(self):
        """Integer CID is converted to string."""
        assert _sanitize_cid(12345) == "12345"

    def test_none_returns_none(self):
        """None returns None."""
        assert _sanitize_cid(None) is None

    def test_nan_returns_none(self):
        """NaN returns None."""
        assert _sanitize_cid(float("nan")) is None

    def test_non_numeric_string_returns_none(self):
        """Non-numeric string returns None."""
        assert _sanitize_cid("abc") is None

    def test_mixed_string_extracts_digits(self):
        """String with mixed characters extracts only digits."""
        assert _sanitize_cid("CID12345") == "12345"

    # --- v0.1.3 ---

    def test_bool_true_does_not_raise(self):
        """bool True does not raise — returns None or a string safely."""
        result = _sanitize_cid(True)
        assert result is None or isinstance(result, str)

    def test_bool_false_does_not_raise(self):
        """bool False does not raise — returns None or a string safely."""
        result = _sanitize_cid(False)
        assert result is None or isinstance(result, str)

    def test_list_does_not_raise(self):
        """list input does not raise — returns None."""
        assert _sanitize_cid([1, 2, 3]) is None

    def test_dict_does_not_raise(self):
        """dict input does not raise — returns None or a string safely."""
        result = _sanitize_cid({"cid": 123})
        assert result is None or isinstance(result, str)


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

    def test_drops_unnamed_index_columns(self):
        """CSV index artifacts are removed during load."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv",
                                         delete=False, encoding="utf-8") as f:
            f.write("Unnamed: 0,Unnamed_0,Unnamed-1,id,SMILES\n0,0,0,1,CCO\n")
            path = f.name
        try:
            df = load_table(path)
            assert "Unnamed: 0" not in df.columns
            assert "Unnamed_0" not in df.columns
            assert "Unnamed-1" not in df.columns
            assert list(df.columns) == ["id", "SMILES"]
        finally:
            os.unlink(path)

    # --- v0.1.3 ---

    def test_nonexistent_file_raises_file_not_found(self):
        """Non-existent file raises FileNotFoundError with path in message."""
        with pytest.raises(FileNotFoundError, match="not found"):
            load_table("this_file_does_not_exist_xyz.csv")

    def test_empty_file_raises_value_error(self):
        """CSV with only a header (zero rows) raises ValueError."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv",
                                         delete=False, encoding="utf-8") as f:
            f.write("id,SMILES\n")
            path = f.name
        try:
            with pytest.raises(ValueError, match="zero rows"):
                load_table(path)
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

    def test_saves_csv_without_index(self):
        """DataFrame indexes are not persisted as CSV columns."""
        df = pd.DataFrame({"SMILES": ["CCO"]}, index=[99])
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
            path = f.name
        try:
            save_table(df, path)
            df2 = pd.read_csv(path)
            assert list(df2.columns) == ["SMILES"]
        finally:
            os.unlink(path)

    def test_rejects_unsafe_traversal_output_path(self):
        """Traversal output paths are rejected at the write boundary."""
        df = pd.DataFrame({"SMILES": ["CCO"]})
        with pytest.raises(ValueError, match="traversal"):
            save_table(df, os.path.join("results", "..", "unsafe.csv"))

    def test_rejects_forward_slash_traversal_output_path(self):
        """Forward-slash traversal is rejected on every host OS."""
        df = pd.DataFrame({"SMILES": ["CCO"]})
        with pytest.raises(ValueError, match="traversal"):
            save_table(df, "../outside.csv")

    def test_rejects_backslash_traversal_output_path(self):
        """Backslash traversal is rejected on every host OS."""
        df = pd.DataFrame({"SMILES": ["CCO"]})
        with pytest.raises(ValueError, match="traversal"):
            save_table(df, r"..\outside.csv")

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
