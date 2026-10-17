# Contributing

Use Python 3.11+ and create/activate a virtual environment as described in
[the installation guide](docs/INSTALLATION.md). Install the reviewed tools and
runtime dependencies from the hash lock before installing the editable package:

```bash
python -m pip install --require-hashes -r requirements-dev.lock
python -m pip install --no-build-isolation --no-deps -e .
python -m pytest
python -m ruff check src tests scripts
python -m mypy src/verbatim_md
python scripts/demo.py --out artifacts/demo
```

The lock includes the build backend and wheel tooling. Avoid hidden dependency
resolution during release checks. For intended dependency updates, change the
constraints in `pyproject.toml`, regenerate `uv.lock` and `requirements-dev.lock`
with uv, then review the diff, dependency advisories and licenses. Conversion
itself never uses uv or a package manager.

Add focused unit, integration or regression coverage for behavior changes.
Validate and build every example when changing the format. Test against the
installed package; if a development environment does not process editable `.pth`
files, diagnose the environment or explicitly set `PYTHONPATH=src` for source
checks, then separately verify a wheel installation outside the checkout.

For reproducible distributions using the same source and locked build tools:

```bash
# macOS/Linux; PowerShell: $env:SOURCE_DATE_EPOCH='1729123200'
export SOURCE_DATE_EPOCH=1729123200
python scripts/reproducible_build.py
python -m twine check dist/*
```

The wrapper canonicalizes generated source-archive metadata; ordinary
`python -m build` is supported but does not normalize sdist timestamps. See
[the release checklist](docs/RELEASE_CHECKLIST.md) for clean-wheel installation,
archive review and actual compatibility gates.

Evidence integrity takes precedence over appearance. Never normalize, truncate,
rewrite or silently repair quotation text. Schema objects remain immutable;
formatting stays separate. Preserve clear distinctions between source-verification
declarations, internal preservation, structural DOCX validation and interactive
Word/Verbatim verification. Record primary sources for compatibility claims and
label inferred or untested behavior.

Discuss format changes and renderer contracts before implementation. Record
consequential choices in architectural decision records. Keep modules focused and
avoid additional dependencies without a clear maintenance benefit. Parallel agents
or contributors must own disjoint files and coordinate shared interfaces first.

Do not contribute proprietary templates, copied Verbatim code, unlicensed
quotations, credentials or private debate files. Examples should use original
pedagogic text with unverified provenance. Report security issues privately to the
repository maintainers once a hosted repository has an established contact; do
not publish exploit payloads containing private material. See the security review
for current boundaries.

Release contributors must rerun clean-wheel installation and example exports,
review licenses and the manual compatibility status, and complete the release
checklist. Publishing packages, public repositories or releases requires explicit
maintainer authorization.
