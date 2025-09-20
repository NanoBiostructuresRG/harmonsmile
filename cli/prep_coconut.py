import argparse
from harmonsmile.pipelines import CoconutPrep

def parse():
    p = argparse.ArgumentParser()
    p.add_argument("--in",  dest="inp", required=True)
    p.add_argument("--smiles", dest="smiles_col", required=True)
    p.add_argument("--out", dest="out", required=True)
    return p.parse_args()

def main():
    a = parse()
    CoconutPrep(a.inp, a.smiles_col, a.out).run()

if __name__ == "__main__":
    main()
