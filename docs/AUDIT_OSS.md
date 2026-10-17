# Independent software engineering and OSS audit

Audit B, 2026-10-17. Reviewer: separate audit agent with no production-code ownership. Production fixes were implemented by the lead; this reviewer owns the security regression tests and this report.

## Findings and regression results

`PYTHONPATH=src .venv/bin/python -m pytest tests/regression/test_security.py -q`: **18 passed** after integration fixes. Ruff passed for the regression file.

The audit reproduced and required fixes for:

- Invalid/truncated ZIPs, missing OOXML parts, malformed XML and malformed manifest schemas escaping the CLI error boundary. They now yield actionable errors and JSON exit status 2.
- Incorrect profile highlight types raising `TypeError`. They now raise validation errors.
- `api.build(strict=True)` ignoring unverified-source warnings. Strict API conversion now refuses publication.
- A nested symlink beneath batch output escaping the selected destination. Static destination escape is now rejected.
- A reference template renaming an expected citation style while retaining its identifier, causing a later `KeyError`. Known imported style names/types are now checked.
- Added table text escaping top-level paragraph-only preservation checks. Such unsupported content cannot claim complete internal preservation.

Macro-part template rejection and no-publication-on-failure also passed. Inspection remains passive: no URLs, macros or relationships are executed. Local directories are not a secure sandbox against another process concurrently replacing path components; use a private output directory for hostile local environments.

## Dependencies and packaging

Initial wheel and source builds succeeded, but source packaging omitted contributor assets and the first build occurred before README existed. The lead added an explicit source manifest and documented source assets. Build-system requirements and CI were adjusted to use locked build tools with `--no-isolation` and `--no-build-isolation` after installing hash-locked dependencies.

An actual PyPI advisory scan found setuptools 82.0.1 affected by [PYSEC-2026-3447](https://osv.dev/vulnerability/PYSEC-2026-3447), fixed in 83.0.0. This affects source-distribution exclusion matching on macOS; see the [upstream advisory](https://github.com/pypa/setuptools/security/advisories/GHSA-h35f-9h28-mq5c). The audit required raising the constraint and regenerating locks before release. Final rescan and artifact results are recorded below after integration.

The original package is MIT. It incorporates no upstream Verbatim VBA/template assets and does not package the user's brief. Dependencies are separately installed and retain their own licenses. Documentation must inventory defusedxml in addition to python-docx, PyYAML, lxml and typing_extensions. Future vendored binaries or executable bundles need a fresh notice inventory.

## External gates

The configured Linux/macOS/Windows CI matrix is not evidence of completed runs on all platforms. Public package-name availability, GitHub remote setup, private security reporting, public release approval and live Word/Verbatim macro compatibility remain external actions. No publication was performed by this audit.

## Final independent recheck

**No unresolved release-blocking software/security findings from this audit.** External compatibility and publication gates above remain open by design.

- Final source tests in this audit: **18/18 security regressions passed**; Ruff clean.
- `python -m build --no-isolation`: wheel and sdist built successfully with fixed tooling.
- `python -m twine check dist/*`: both distributions **passed**, with README metadata present.
- Updated `pip-audit --disable-pip --no-deps -r requirements-dev.lock`: **no known vulnerabilities found**. This is a time-bounded advisory lookup, not a proof that dependencies have no defects.
- Inspected sdist: **82 members**, including docs, skills, tests, examples, profiles and CI; no brief, `.dotm`, artifacts directory or virtual environment.
- Inspected wheel: **17 members**, including package and MIT license; no evidence documents or Verbatim templates.
- Installed wheel into a separate `/tmp` virtual environment, ran CLI outside the checkout, then validated, built and inspected `examples/single-card.md`: **passed**, one card internally preserved.
- Reproducible double-build comparison is owned by lead integration; this reviewer verified build/install/package contents independently.

The security-best-practices skill was consulted. Its reference catalog contains Python web-framework guidance rather than a Python CLI guide; this audit therefore used direct local-file, YAML, XML, ZIP, dependency, template, atomic-publication and packaging checks appropriate to this program.

## Final packaging and Word-workflow follow-up

Independently reviewed `scripts/reproducible_build.py`: it invokes locked build tools
without isolation/network dependency resolution, sorts generated archive members,
normalizes tar ownership/mode/timestamps and gzip metadata, rejects traversal and
non-file/non-directory members, and never extracts archive paths. It operates on
generated build artifacts, not arbitrary user input. The metadata regression test
passed. Source reproducibility comparisons are recorded by the lead.

Rechecked the final `artifacts/repro-d` wheel and source archive: both passed Twine.
The source archive has **92 members**, includes the build wrapper and source assets,
and all members have canonical epoch/ownership metadata. No private brief or
Verbatim macro template is included. Installed that final wheel into a fresh,
separate `/tmp` virtual environment and ran validate → build → inspect `--against`
outside the checkout: **passed**, with text preservation true and formatting
verification explicitly false. Security regressions plus archive normalization:
**19 passed**. Ruff passed for the wrapper and its test.

`inspect --against` provides an external canonical comparison when Word discards
the embedded manifest; it does not authenticate sources or certify formatting.
The lead's recorded Word 16.114/macOS experiment includes successful one-card
open/navigation/save/reopen and exact text after Verbatimize. It also records
an actual Debate Shrink ribbon failure (VBA 5852 before dispatch). This remains
an explicit interactive compatibility limitation. Neither these packaging checks
nor the limited Word experiment establish universal Verbatim macro compatibility.
