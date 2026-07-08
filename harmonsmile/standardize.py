# SPDX-License-Identifier: LGPL-3.0-or-later
"""
SMILES standardization utilities based on RDKit.

Provides :class:`RDKitStandardizer` for converting SMILES strings to
canonical + isomeric + Kekulized form and for applying the v0.3.0
RDKit-native lab harmonization policy.
"""

from __future__ import annotations

from dataclasses import dataclass

from rdkit import Chem
from rdkit.Chem.MolStandardize import rdMolStandardize


@dataclass(frozen=True)
class HarmonizationResult:
    """
    Result from lab SMILES harmonization.

    Attributes
    ----------
    value : str or None
        Harmonized SMILES when status is ok.
    status : str
        Processing status.
    error : str or None
        Human-readable error detail for failures.
    warning : str or None
        Warning detail for successful outputs with caveats.
    """

    value: str | None
    status: str
    error: str | None
    warning: str | None


class RDKitStandardizer:
    """
    Standardize and harmonize SMILES strings using RDKit.

    ``to_iso_kek`` preserves the v0.2.5 RDKit canonicalization contract.
    ``to_lab_harmonized`` applies the v0.3.0 lab harmonization policy.
    """

    _ALLOWED_ELEMENTS = frozenset({
        "H", "B", "C", "N", "O", "F", "Si", "P", "S", "Cl", "Se", "Br", "I",
    })

    @staticmethod
    def to_iso_kek(smiles: str) -> str | None:
        """
        Convert SMILES to canonical + isomeric + Kekulized form.

        Parameters
        ----------
        smiles : str
            Input SMILES string.

        Returns
        -------
        str or None
            Standardized SMILES, or None if input is invalid.
        
        Notes
        -----
        This is a compatibility canonicalization layer, not full chemical
        harmonization. It does not intentionally desalt, neutralize, reionize,
        or canonicalize tautomers.

        Chiral centers (e.g. ``[C@@H]``) are preserved because RDKit encodes
        tetrahedral stereochemistry independently of kekulization.

        E/Z geometry on double bonds (``/`` and ``\\`` in SMILES) is preserved
        only when RDKit can unambiguously determine the configuration after
        parsing and sanitization. For some double bonds — particularly those
        in conjugated systems or where the source SMILES omits directional
        bonds on one side — RDKit cannot resolve the geometry and silently
        drops the ``/`` and ``\\`` notation. This is a known RDKit behavior, not a
        bug in harmonsmile. If E/Z fidelity is critical for your use case,
        validate ``SMILES_RDKit`` against the source SMILES.

        Examples
        --------
        >>> RDKitStandardizer.to_iso_kek("c1ccccc1")
        'C1=CC=CC=C1'
        >>> RDKitStandardizer.to_iso_kek("invalid")
        >>> RDKitStandardizer.to_iso_kek("")
        """
        if not isinstance(smiles, str) or not smiles.strip():
            return None
        m = Chem.MolFromSmiles(smiles, sanitize=True)
        if m is None:
            return None
        try:
            return Chem.MolToSmiles(m, canonical=True, isomericSmiles=True, kekuleSmiles=True)
        except Exception:
            return None

    @staticmethod
    def to_conn_kek(smiles: str) -> str | None:
        """
        Convert SMILES to canonical + connectivity-only + Kekulized form.

        Stereochemistry is stripped. Useful for connectivity-based comparisons
        where chirality is not relevant.

        Parameters
        ----------
        smiles : str
            Input SMILES string.

        Returns
        -------
        str or None
            Standardized SMILES without stereochemistry, or None if invalid.

        Examples
        --------
        >>> RDKitStandardizer.to_conn_kek("C[C@@H](O)F")
        'CC(O)F'
        >>> RDKitStandardizer.to_conn_kek("invalid")
        >>> RDKitStandardizer.to_conn_kek("")
        """
        if not isinstance(smiles, str) or not smiles.strip():
            return None
        m = Chem.MolFromSmiles(smiles, sanitize=True)
        if m is None:
            return None
        try:
            return Chem.MolToSmiles(m, canonical=True, isomericSmiles=False, kekuleSmiles=True)
        except Exception:
            return None

    @classmethod
    def to_lab_harmonized(
        cls,
        smiles,
        *,
        canonicalize_tautomers: bool = True,
        max_tautomers: int = 1000,
        max_transforms: int = 1000,
    ) -> HarmonizationResult:
        """
        Harmonize a SMILES string using explicit RDKit-native lab policy.

        The policy is intentionally auditable and avoids broad parent/cleanup
        helpers. It validates input, parses with RDKit sanitization, applies
        normalization, selects the largest fragment, validates allowed elements,
        uncharges, reionizes, optionally canonicalizes tautomers, and finally
        serializes as canonical, isomeric, Kekule SMILES.

        Parameters
        ----------
        smiles : Any
            Input SMILES value.
        canonicalize_tautomers : bool, optional
            If True, use RDKit TautomerEnumerator canonicalization.
        max_tautomers : int, optional
            Applied through TautomerEnumerator.SetMaxTautomers when available.
        max_transforms : int, optional
            Applied through TautomerEnumerator.SetMaxTransforms when available.

        Returns
        -------
        HarmonizationResult
            Typed harmonization result with value, status, error, and warning.

        Notes
        -----
        This method does not call RemoveStereochemistry. When available, RDKit
        tautomer stereo-removal defaults are overridden to preserve bond and
        sp3 stereo, and stereo reassignment is kept enabled. Residual assigned
        chiral-center changes after tautomer canonicalization are reported as
        warning="stereo_annotation_changed". This is a conservative caveat, not
        a complete stereochemistry audit. The method returns one canonical
        harmonized representation, not a tautomer ensemble, and it is not a
        pH-specific or bioactive-tautomer predictor.
        """
        if not isinstance(smiles, str) or not smiles.strip():
            return HarmonizationResult(
                None,
                "missing_smiles",
                "missing or blank SMILES",
                None,
            )

        mol = Chem.MolFromSmiles(smiles, sanitize=True)
        if mol is None:
            return HarmonizationResult(None, "invalid_smiles", "invalid SMILES", None)

        try:
            mol = rdMolStandardize.Normalize(mol)
            mol = rdMolStandardize.LargestFragmentChooser().choose(mol)

            disallowed = cls._disallowed_elements(mol)
            if disallowed:
                symbols = ", ".join(disallowed)
                return HarmonizationResult(
                    None,
                    "disallowed_elements",
                    f"disallowed elements: {symbols}",
                    None,
                )

            mol = cls._uncharger().uncharge(mol)
            mol = rdMolStandardize.Reionizer().reionize(mol)

            warning = None
            if canonicalize_tautomers:
                before_chiral = cls._assigned_chiral_centers(mol)
                enumerator = cls._tautomer_enumerator(max_tautomers, max_transforms)
                result = enumerator.Enumerate(mol)

                if cls._tautomer_limit_exceeded(result):
                    return HarmonizationResult(
                        None,
                        "tautomer_limit_exceeded",
                        f"tautomer enumeration status: {result.status}",
                        None,
                    )

                mol = enumerator.PickCanonical(result)
                after_chiral = cls._assigned_chiral_centers(mol)
                if before_chiral != after_chiral:
                    warning = "stereo_annotation_changed"

            kekule_mol = Chem.Mol(mol)
            Chem.Kekulize(kekule_mol, clearAromaticFlags=True)
            value = Chem.MolToSmiles(
                kekule_mol,
                canonical=True,
                isomericSmiles=True,
                kekuleSmiles=True,
            )
        except Exception as exc:
            return HarmonizationResult(None, "harmonization_failed", str(exc), None)

        return HarmonizationResult(value, "ok", None, warning)

    @classmethod
    def _disallowed_elements(cls, mol: Chem.Mol) -> list[str]:
        return sorted({
            atom.GetSymbol()
            for atom in mol.GetAtoms()
            if atom.GetSymbol() not in cls._ALLOWED_ELEMENTS
        })

    @staticmethod
    def _uncharger():
        try:
            return rdMolStandardize.Uncharger(canonicalOrder=True)
        except Exception:
            return rdMolStandardize.Uncharger(True)

    @staticmethod
    def _tautomer_enumerator(max_tautomers: int, max_transforms: int):
        enumerator = rdMolStandardize.TautomerEnumerator()

        if hasattr(enumerator, "SetMaxTautomers"):
            enumerator.SetMaxTautomers(max_tautomers)
        if hasattr(enumerator, "SetMaxTransforms"):
            enumerator.SetMaxTransforms(max_transforms)

        if (
            hasattr(enumerator, "GetRemoveBondStereo")
            and hasattr(enumerator, "SetRemoveBondStereo")
            and enumerator.GetRemoveBondStereo()
        ):
            enumerator.SetRemoveBondStereo(False)
        if (
            hasattr(enumerator, "GetRemoveSp3Stereo")
            and hasattr(enumerator, "SetRemoveSp3Stereo")
            and enumerator.GetRemoveSp3Stereo()
        ):
            enumerator.SetRemoveSp3Stereo(False)
        if hasattr(enumerator, "SetReassignStereo"):
            enumerator.SetReassignStereo(True)

        return enumerator

    @staticmethod
    def _tautomer_limit_exceeded(result) -> bool:
        status = getattr(result, "status", None)
        if status is None:
            return False
        names = getattr(rdMolStandardize.TautomerEnumeratorStatus, "names", {})
        limit_statuses = {
            names.get("MaxTautomersReached"),
            names.get("MaxTransformsReached"),
        }
        limit_statuses.discard(None)
        return bool(limit_statuses) and status in limit_statuses

    @staticmethod
    def _assigned_chiral_centers(mol: Chem.Mol) -> tuple[tuple[int, str], ...]:
        try:
            centers = Chem.FindMolChiralCenters(
                mol,
                includeUnassigned=False,
                useLegacyImplementation=False,
            )
        except TypeError:
            centers = Chem.FindMolChiralCenters(mol, includeUnassigned=False)
        return tuple(centers)
