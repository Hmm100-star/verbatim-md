# Release checklist

The local package is an MIT release candidate. Public release requires a separate
maintainer decision; package-name availability has not been established.

1. Install hash-locked dependencies, then install the project without build isolation.
2. Run unit/integration/regression tests, Ruff, mypy, all examples and scripts/demo.py.
3. Read both independent audit reports and FINAL_AUDIT.md. Resolve software blockers.
4. Recheck dependency advisories and license inventory. Do not bundle upstream Verbatim assets.
5. Build wheel/sdist with locked tools and SOURCE_DATE_EPOCH; compare repeated builds.
6. Check Twine metadata and install the wheel in a fresh environment outside the checkout.
7. Inspect archive members for private evidence, templates, credentials and unrelated files.
8. Record actual OS/Word/Verbatim workflow results. The observed ribbon error 5852 remains
   a blocker to claiming full interactive Verbatim compatibility, even if releasing the
   explicitly limited structural converter as a release candidate is acceptable.
9. Configure a GitHub remote, private vulnerability reporting and protected publication
   credentials only after maintainer authorization. Review repository/package names.
10. Obtain authorization before public repository creation, publishing or tagging a release.

Reproducible development build:

```bash
python -m pip install --require-hashes -r requirements-dev.lock
python -m pip install --no-build-isolation --no-deps -e .
# macOS/Linux; on PowerShell use $env:SOURCE_DATE_EPOCH='1729123200'
export SOURCE_DATE_EPOCH=1729123200
python scripts/reproducible_build.py
python -m twine check dist/*
```

The GitHub release workflow produces review artifacts only and never publishes.
CI is configured for Linux/macOS/Windows and Python 3.11–3.13; configuration is
not proof of completed remote CI runs. Runtime conversion is offline after install.

The wrapper builds with the installed locked tools, fixes wheel timestamps via
SOURCE_DATE_EPOCH, and canonicalizes sdist member ordering, timestamps, modes,
ownership and gzip metadata without extracting paths. Standard `python -m build`
remains supported, but its unnormalized sdist timestamps are not byte reproducible.
