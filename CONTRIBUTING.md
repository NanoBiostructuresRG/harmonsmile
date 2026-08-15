# Contributing to HARMONSMILE

Thank you for your interest in contributing to HARMONSMILE!  
This project is maintained by the [NanoBiostructures Research Group](https://nanobiostructuresrg.github.io) at Tecnológico de Monterrey.

## How to contribute

### Reporting bugs
Open an issue on [GitHub Issues](https://github.com/NanoBiostructuresRG/harmonsmile/issues) with:
- A clear description of the problem
- A minimal reproducible example
- Your environment details (OS, Python version, RDKit version)

### Suggesting features
Open an issue with the `enhancement` label describing:
- The use case
- Why it would be useful beyond your specific workflow

### Submitting a pull request
1. Fork the repository
2. Create a branch from `main`: `git switch -c dev/your-feature`
3. Make your changes
4. Run the test suite: `pytest tests/`
5. Push your branch and open a pull request against `main`

Pull requests should pass CI before merge. User-facing changes should include
appropriate documentation and changelog updates.

## Development setup

Create an environment with Python 3.11 or newer using the tool you prefer
(conda, venv, uv, or similar), then install the package in editable mode with
its development dependencies:

```bash
git clone https://github.com/NanoBiostructuresRG/harmonsmile.git
cd harmonsmile
python -m pip install -e ".[dev]"
```

RDKit is resolved automatically as a package dependency. To build the
documentation locally, install the `docs` extra as well:

```bash
python -m pip install -e ".[dev,docs]"
mkdocs serve
```

## Code style
This project follows [PEP 8](https://peps.python.org/pep-0008/). Please run `ruff` or `flake8` before submitting.

## Documentation and changelog
Update the README, documentation, examples, or API reference when behavior,
interfaces, commands, or examples change. Add an entry to `CHANGELOG.md` for
user-facing changes.

## Scientific and cheminformatics changes
For changes that affect SMILES standardization or cheminformatics assumptions,
explain or cite the relevant assumptions when appropriate. Add or update tests
and examples for changed standardization behavior, document RDKit-dependent
behavior when relevant, and preserve reproducibility of the workflow.

## Questions
Open an issue or contact the maintainer via the repository.
