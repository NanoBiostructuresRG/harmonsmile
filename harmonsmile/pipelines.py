import os
import pandas as pd
from .io import load_table, save_table
from .standardize import RDKitStandardizer
from .pubchem import PubChemClient

def log_error(msg, path="logs/errors.txt"):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(msg + "\n")
    print("[LOG]", msg)

class PubChemIngest:
    def __init__(self, cfg, client=None, std=None):
        self.cfg = cfg
        self.client = client or PubChemClient(logger=lambda m: log_error(m, cfg.error_log))
        self.std = std or RDKitStandardizer()

    def run(self) -> pd.DataFrame:
        df = load_table(self.cfg.input_path)
        props = df[self.cfg.cid_col].apply(
            lambda c: self.client.fetch_props(c, list(self.cfg.props))
        )
        props_df = pd.DataFrame(list(props))
        out = pd.concat([df, props_df], axis=1)

        # SMILES homologation to COCONUT 2.0 convention (RDKit canonical+isomeric+kekulized)
        if "SMILES" in out.columns:
            out["SMILES_RDKit"] = out["SMILES"].apply(self.std.to_iso_kek)
        
        if "MolecularWeight" in out.columns:
            out.rename(columns={"MolecularWeight": "MW"}, inplace=True)
        
        desired = ["id", "PubChem CID", "MW", "SMILES", "SMILES_RDKit"]
        present = [c for c in desired if c in out.columns]
        others  = [c for c in out.columns if c not in present]

        if "MW" in out.columns:
            out["MW"] = pd.to_numeric(out["MW"], errors="coerce")
        
        out = out[present + others]

        save_table(out, self.cfg.output_path)

        n = len(out)
        n_src = out["SMILES"].notna().sum() if "SMILES" in out.columns else 0
        n_rd  = out["SMILES_RDKit"].notna().sum() if "SMILES" in out.columns else 0
        print(f"[OK] {self.cfg.output_path} | SMILES fuente: {n_src}/{n} | RDKit: {n_rd}/{n}")
        return out

class CoconutPrep:
    def __init__(self, input_path: str, smiles_col: str, output_path: str, std=None):
        self.input_path, self.smiles_col, self.output_path = input_path, smiles_col, output_path
        self.std = std or RDKitStandardizer()

    def run(self) -> pd.DataFrame:
        os.makedirs(os.path.dirname(self.output_path) or ".", exist_ok=True)
        df = pd.read_csv(self.input_path, encoding="utf-8-sig")
        if self.smiles_col not in df.columns:
            raise ValueError(f"Column '{self.smiles_col}' not found. Cols: {list(df.columns)}")
        df["SMILES_RDKit"] = df[self.smiles_col].apply(self.std.to_iso_kek)
        df.to_csv(self.output_path, index=False, encoding="utf-8")
        n, n_ok = len(df), df["SMILES_RDKit"].notna().sum()
        print(f"[OK] {self.output_path} | RDKit: {n_ok}/{n}")
        return df
