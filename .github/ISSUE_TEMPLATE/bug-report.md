---
name: Bug Report
about: Report incorrect genetics behavior or a software bug
title: "[Bug] <Brief description>"
labels: "bug"
assignees: ""
---

## What happened?

<!-- Describe the bug clearly. What did you observe? -->

## What did you expect?

<!-- What should have happened instead? If it's a genetics error, cite a source if possible. -->

## How to reproduce

<!-- Minimal code or steps to reproduce the issue: -->

```python
from genetics.horse import Horse

# Paste code that triggers the bug here
horse = Horse.from_string("E:e/e A:A/a ...")
print(horse.phenotype)  # Expected: X, Got: Y
```

## Scientific reference (if applicable)

<!-- Is this a known fact about equine genetics? Link or cite a source. -->

## Environment

- Python version:
- OS:
- How are you running it? (CLI / Streamlit / API / Python import)
