from dataclasses import dataclass

@dataclass
class Config:
    input_path: str
    output_path: str
    error_log: str = "logs/errors.txt"
    id_col: str = "id"
    cid_col: str = "PubChem CID"
    props: tuple[str, ...] = ("SMILES", "MolecularWeight")
