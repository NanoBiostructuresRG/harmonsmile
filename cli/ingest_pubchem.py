import argparse
from harmonsmile.config import Config
from harmonsmile.pipelines import PubChemIngest

def parse():
    p = argparse.ArgumentParser()
    p.add_argument("--in",  dest="inp", required=True)
    p.add_argument("--out", dest="out", required=True)
    p.add_argument("--idcol", default="id")
    p.add_argument("--cidcol", default="PubChem CID")
    return p.parse_args()

def main():
    a = parse()
    cfg = Config(input_path=a.inp, output_path=a.out, id_col=a.idcol, cid_col=a.cidcol)
    PubChemIngest(cfg).run()

if __name__ == "__main__":
    main()
