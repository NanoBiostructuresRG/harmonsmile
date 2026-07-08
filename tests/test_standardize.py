# SPDX-License-Identifier: LGPL-3.0-or-later
"""Unit tests for harmonsmile.standardize."""

from harmonsmile import HarmonizationResult, RDKitStandardizer


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


class TestToLabHarmonized:
    """Tests for RDKitStandardizer.to_lab_harmonized."""

    def test_missing_none_input(self):
        result = RDKitStandardizer.to_lab_harmonized(None)
        assert result == HarmonizationResult(
            None,
            "missing_smiles",
            "missing or blank SMILES",
            None,
        )

    def test_blank_input(self):
        result = RDKitStandardizer.to_lab_harmonized("   ")
        assert result.status == "missing_smiles"
        assert result.error == "missing or blank SMILES"
        assert result.value is None

    def test_non_string_input(self):
        result = RDKitStandardizer.to_lab_harmonized(123)
        assert result.status == "missing_smiles"
        assert result.error == "missing or blank SMILES"
        assert result.value is None

    def test_invalid_smiles(self):
        result = RDKitStandardizer.to_lab_harmonized("invalid_smiles")
        assert result.status == "invalid_smiles"
        assert result.error == "invalid SMILES"
        assert result.value is None

    def test_simple_valid_molecule(self):
        result = RDKitStandardizer.to_lab_harmonized("CCO")
        assert result.status == "ok"
        assert result.value == "CCO"
        assert result.warning is None

    def test_largest_fragment_ignores_removed_counterion_for_elements(self):
        result = RDKitStandardizer.to_lab_harmonized("[Na+].CCO")
        assert result.status == "ok"
        assert result.value == "CCO"

    def test_disallowed_element_in_largest_fragment(self):
        result = RDKitStandardizer.to_lab_harmonized("[Zn]CCCC")
        assert result.status == "disallowed_elements"
        assert result.value is None
        assert result.error is not None
        assert "Zn" in result.error

    def test_isotope_of_allowed_element_is_allowed(self):
        result = RDKitStandardizer.to_lab_harmonized("[13CH4]")
        assert result.status == "ok"
        assert result.value is not None
        assert "13C" in result.value

    def test_charged_molecule_exercises_uncharge_reionize(self):
        result = RDKitStandardizer.to_lab_harmonized("C[NH+](C)C")
        assert result.status == "ok"
        assert result.value == "CN(C)C"

    def test_canonicalize_tautomers_true_and_false_are_accepted(self):
        yes = RDKitStandardizer.to_lab_harmonized("CC(=O)C", canonicalize_tautomers=True)
        no = RDKitStandardizer.to_lab_harmonized("CC(=O)C", canonicalize_tautomers=False)
        assert yes.status == "ok"
        assert no.status == "ok"
        assert yes.value is not None
        assert no.value is not None

    def test_aromatic_output_is_kekule(self):
        result = RDKitStandardizer.to_lab_harmonized("c1ccccc1")
        assert result.status == "ok"
        assert result.value is not None
        assert "=" in result.value
        assert "c" not in result.value

    def test_tautomer_enumerator_stereo_flags_preserve_annotations(self):
        enumerator = RDKitStandardizer._tautomer_enumerator(1000, 1000)
        assert enumerator.GetRemoveBondStereo() is False
        assert enumerator.GetRemoveSp3Stereo() is False
        assert enumerator.GetReassignStereo() is True

    def test_tautomer_limit_exceeded_when_rdkit_reports_limit_status(self):
        result = RDKitStandardizer.to_lab_harmonized(
            "CC(=O)C",
            max_tautomers=1,
            max_transforms=1,
        )
        assert result.status == "tautomer_limit_exceeded"
        assert result.value is None

    def test_tautomer_limit_exceeded_false_without_status(self):
        class ResultWithoutStatus:
            pass

        assert RDKitStandardizer._tautomer_limit_exceeded(ResultWithoutStatus()) is False

    def test_stereochemistry_preserved_for_simple_chiral_center(self):
        result = RDKitStandardizer.to_lab_harmonized("C[C@@H](O)F")
        assert result.status == "ok"
        assert result.value is not None
        assert "@" in result.value
        assert result.warning is None


class TestLegacyBehaviorPreserved:
    """Explicit guard tests for legacy standardization methods."""

    def test_to_iso_kek_still_behaves_as_before(self):
        assert RDKitStandardizer.to_iso_kek("c1ccccc1") == "C1=CC=CC=C1"
        assert RDKitStandardizer.to_iso_kek("invalid_smiles") is None

    def test_to_conn_kek_still_behaves_as_before(self):
        assert RDKitStandardizer.to_conn_kek("C[C@@H](O)F") == "CC(O)F"
        assert RDKitStandardizer.to_conn_kek("invalid_smiles") is None
