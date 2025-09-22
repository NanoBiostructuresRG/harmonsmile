# HARMONSMILE: Harmonize SMILES
**Version 1.0.0 – September, 2025. Monterrey**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

[![Version](https://img.shields.io/badge/version-v1.0-blue.svg)]()

---

## Description
**HARMONSMILE** is a toolkit for aligns SMILES to the convention: canonical + isomeric + keculized (e.g., RDKit, COCONUT 2.0).

---

## Purpose
The primary objective of HARMONSMILE is to automate the preparation of SMILES for cheminformatics workflows and **phase 1** machine learning applications within the computational drug discovery pipeline. The platform enables:
- **Standardized SMILES** for comparing several versions.
- **Facilitate reproducibility** in academic and industrial experiments.

---

## Project Structure
```text
HARMONSMILE/Phase 1
│
├── cli/
│   ├── harmonize.py
│   ├── ingest_pubchem.py                      
│   └── prep_coconut.py    
│
├── data/
│   ├── database1.csv                   # Database1 Pubchem
│   ├── database2.csv                   # Database2 COCONUT
│   └── database3.csv                   # Database3 Independent
│
├── harmonsmile/                        
│   ├── __init__.py
│   ├── __main__.py
│   ├── config.py
│   ├── io.py
│   ├── pipelines.py
│   ├── pubchem.py
│   └── standardize.py        
├── logs/                            
├── results/                     
│   ├── database1_homosmiles.csv
│   ├── database2_homosmiles.csv
│   └── database3_homosmiles.csv 
│   
└── README.md                           
```

---

## How to Run
From the project root directory, run the following command:

```bash
# Only database1
python -m harmonsmile --pubchem-in data/database1.csv --pubchem-out results/database_homosmiles.csv

# Only database2
python -m harmonsmile --coconut-in data/database2.csv --coconut-smiles SMILES --coconut-out results/database2_homosmiles.csv

# Only database3
python -m harmonsmile --coconut-in data/database3.csv --coconut-smiles SMILES --coconut-out results/database3_homosmiles.csv

# All 1&2&3
python -m harmonsmile first \ second

```

---

## Output

The following files will be saved under the `results/` directory:

- `database1_homosmiles.csv`
- `database2_homosmiles.csv`
- `database3_homosmiles.csv`  

---

## Example Console Output

```text
[OK] results\database1_homosmiles.csv | SMILES fuente: 66/66 | RDKit: 66/66

```

---

## Notes

- The PubChem dataset should contain two columns: id, PubChem CID
- The COCONUT dataset should contain at least two columns: id, SMILES
- The Independent dataset should contain at least two columns: id, SMILES
---

## Future Extensions

- Add more sources (e.g., ChEMBL) with the same RDKit normalization → unified SMILES_RDKit output.
- ML-ready features: standardized pipeline to generate ECFP (with/without chirality), plus InChI/InChIKey for dedup & robust matching.

---

## Author

Developed by **Flavio F. Contreras-Torres** (Tecnológico de Monterrey)  
Monterrey, Mexico – September 2025

---

## License
This project is licensed under the terms of the [MIT License](https://github.com/NanoBiostructuresRG/molraptor/blob/main/LICENSE).  
See the LICENSE file for full details.