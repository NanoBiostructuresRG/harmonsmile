# SPDX-License-Identifier: LGPL-3.0-or-later
"""Unit tests for harmonsmile.standardize."""

import pytest
from harmonsmile import RDKitStandardizer


class TestToIsoKek:
    """Tests for RDKitStandardizer.to_iso_kek."""

    def test_benzene(self):
        """Aromatic SMILES converts to Kekulized form."""
        assert RDKitStandardizer.to_iso_kek("c1ccccc1") == "C1=CC=CC=C1"

    def test_isomeric_preserved(self):
        """Stereochemistry is preserved."""
        result = RDKitStandardizer.to_iso_kek("C[C@@H](O)F")
        assert result is not None
        assert "@" in result

    def test_invalid_smiles_returns_none(self):
        """Invalid SMILES returns None."""
        assert RDKitStandardizer.to_iso_kek("invalid_smiles") is None

    def test_empty_string_returns_none(self):
        """Empty string returns None."""
        assert RDKitStandardizer.to_iso_kek("") is None

    def test_whitespace_only_returns_none(self):
        """Whitespace-only string returns None."""
        assert RDKitStandardizer.to_iso_kek("   ") is None

    def test_non_string_returns_none(self):
        """Non-string input returns None."""
        assert RDKitStandardizer.to_iso_kek(None) is None
        assert RDKitStandardizer.to_iso_kek(123) is None

    def test_canonical_output(self):
        """Different representations of the same molecule give the same output."""
        a = RDKitStandardizer.to_iso_kek("OCC")
        b = RDKitStandardizer.to_iso_kek("CCO")
        assert a == b
        assert a is not None


class TestToConnKek:
    """Tests for RDKitStandardizer.to_conn_kek."""

    def test_benzene(self):
        """Aromatic SMILES converts to Kekulized form."""
        assert RDKitStandardizer.to_conn_kek("c1ccccc1") == "C1=CC=CC=C1"

    def test_stereochemistry_stripped(self):
        """Stereochemistry is removed."""
        result = RDKitStandardizer.to_conn_kek("C[C@@H](O)F")
        assert result is not None
        assert "@" not in result

    def test_invalid_smiles_returns_none(self):
        """Invalid SMILES returns None."""
        assert RDKitStandardizer.to_conn_kek("invalid_smiles") is None

    def test_empty_string_returns_none(self):
        """Empty string returns None."""
        assert RDKitStandardizer.to_conn_kek("") is None

    def test_whitespace_only_returns_none(self):
        """Whitespace-only string returns None."""
        assert RDKitStandardizer.to_conn_kek("   ") is None

    def test_non_string_returns_none(self):
        """Non-string input returns None."""
        assert RDKitStandardizer.to_conn_kek(None) is None
        assert RDKitStandardizer.to_conn_kek(123) is None

    def test_enantiomers_give_same_output(self):
        """R and S enantiomers produce the same connectivity SMILES."""
        r = RDKitStandardizer.to_conn_kek("C[C@@H](O)F")
        s = RDKitStandardizer.to_conn_kek("C[C@H](O)F")
        assert r == s
        assert r is not None
