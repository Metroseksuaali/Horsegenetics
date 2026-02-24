# Contributing to Horse Genetics

Thank you for considering contributing! This project welcomes bug fixes,
genetics accuracy improvements, and new features.

## How to contribute

1. **Fork** the repository
2. Create a feature branch: `git checkout -b fix/description-of-fix`
3. Make your changes
4. Run the test suite: `pytest test_genetics.py -v`
5. **If changing genetics logic** — cite your source (UC Davis VGL, PubMed, Etalon, etc.)
6. Open a Pull Request with a clear description

## What to contribute

### High-value contributions

- **Genetics accuracy fixes** — wrong phenotype for a gene combination?
  Open a bug report with a scientific reference, or submit a fix directly.
- **New genes** — add a gene to `genetics/gene_definitions.py` and update
  `genetics/gene_interaction.py` with the interaction rules.
- **New tests** — improve test coverage, especially for rare combinations.
- **Language support** — the `locales/` directory contains UI translations.

### Genetics accuracy standard

All genetics logic should be based on peer-reviewed research or trusted
sources such as:

- UC Davis Veterinary Genetics Laboratory: https://vgl.ucdavis.edu/
- Etalon Diagnostics: https://etalondx.com/
- PubMed (search for MC1R, ASIP, SLC45A2, TBX3, PMEL17, etc.)

When adding or fixing genetics behavior, please include a reference to
your source in the PR description or as a code comment.

## Running tests

```bash
pytest test_genetics.py -v        # Run all 118 genetics tests
pytest test_performance.py        # Performance benchmarks
```

All tests must pass before a PR will be merged.

## Code style

- Python 3.9+
- Follow existing naming conventions (snake_case functions, PascalCase classes)
- Docstrings for public functions
- No external dependencies in the core `genetics/` package (stdlib only)

## Reporting bugs

Use the **Bug Report** issue template on GitHub. For genetics accuracy bugs,
please include a scientific reference so the fix can be verified.

## Showing your project

If you built something with Horse Genetics, please open a
**Show and Tell** issue — we'd love to see what you made!
