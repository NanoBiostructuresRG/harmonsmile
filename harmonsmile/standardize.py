from rdkit import Chem

class RDKitStandardizer:
    @staticmethod
    def to_iso_kek(smiles: str) -> str | None:
        if not isinstance(smiles, str) or not smiles.strip(): return None
        m = Chem.MolFromSmiles(smiles, sanitize=True)
        if m is None: return None
        return Chem.MolToSmiles(m, canonical=True, isomericSmiles=True, kekuleSmiles=True)

    @staticmethod
    def to_conn_kek(smiles: str) -> str | None:
        if not isinstance(smiles, str) or not smiles.strip(): return None
        m = Chem.MolFromSmiles(smiles, sanitize=True)
        if m is None: return None
        return Chem.MolToSmiles(m, canonical=True, isomericSmiles=False, kekuleSmiles=True)
