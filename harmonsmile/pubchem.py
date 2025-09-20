import time
import requests

class PubChemClient:
    def __init__(self, logger=print, sleep=0.2, retries=3):
        self.log, self.sleep, self.retries = logger, sleep, retries

    def fetch_props(self, cid: str, props: list[str]) -> dict:
        if not cid: return {p: None for p in props}
        base = "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid"
        url = f"{base}/{cid}/property/{','.join(props)}/JSON"
        for k in range(self.retries):
            try:
                r = requests.get(url, timeout=12, headers={"User-Agent":"python-requests"})
                r.raise_for_status()
                row = r.json()["PropertyTable"]["Properties"][0]
                return {p: row.get(p) for p in props}
            except Exception as e:
                if k + 1 == self.retries:
                    self.log(f"[PubChem] CID {cid}: {e}")
                    return {p: None for p in props}
                time.sleep(self.sleep * (2 ** k))
            finally:
                time.sleep(self.sleep)
