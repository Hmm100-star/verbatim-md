# Installation and first export

Verbatim-MD needs Python 3.11 or later. It generates DOCX on Windows, macOS and
Linux without Word or Verbatim. Word plus a legitimate Verbatim installation is
needed for the interactive debate workflow. Read [the compatibility results](COMPATIBILITY.md)
before relying on macros: the tested local Debate ribbon encountered error 5852.
The package has not been publicly published; install this checkout or a reviewed
local wheel rather than assuming a package-index release exists.

## Install this checkout

Open a terminal in the repository directory. On macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install .
```

On Windows PowerShell:

```powershell
py -3 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install .
```

If local PowerShell policy prevents activation, use `.venv\Scripts\python.exe`
instead of `python` and `.venv\Scripts\verbatim-md.exe` instead of `verbatim-md`.
No system policy change is required. macOS/Linux can likewise use
`.venv/bin/python` and `.venv/bin/verbatim-md` without activation.

A normal source installation may download build tools and runtime dependencies.
Conversion works fully offline after installation. Citation URLs are stored
metadata and are never fetched; there are no API keys or database services.

## First export

```bash
verbatim-md validate examples/single-card.md
verbatim-md build examples/single-card.md -o single-card.docx
verbatim-md inspect single-card.docx --json
```

The tutorial evidence is original demonstration text and intentionally unverified.
Its warnings are expected. `--strict` turns warnings into failure; do not mark a
source verified merely to remove a warning. Existing output files are protected.
Use `--force` only when you intend to replace an existing destination.

After Word editing, compare against the original quotation text:

```bash
verbatim-md inspect word-edited.docx --against examples/single-card.md --json
```

Word may remove the embedded integrity manifest. `--against` compares text/order
against supplied canonical Markdown without relying on that manifest; it does
not authenticate the source or certify formatting/macro behavior.

Batch conversion keeps relative input paths. Place the output outside the input
directory:

```bash
verbatim-md build-all examples --out converted-examples --profile ld --json
```

Exit `0` means success; `1` means a failed report, strict warning or batch item;
`2` means a usage, malformed-input, configuration or filesystem error. JSON
reports are available with `--json`. Use `--verbose` before the command for
tracebacks while diagnosing errors. The module form
`python -m verbatim_md.cli --help` also works in an installed environment.

## Install a reviewed wheel

A contributor can build the wheel using the locked instructions in
[CONTRIBUTING.md](../CONTRIBUTING.md). In a fresh virtual environment:

```bash
python -m pip install dist/verbatim_md-0.1.0-py3-none-any.whl
```

The wheel itself is platform independent; separately installed dependency wheels
must match the Python version, operating system and architecture. Built-in
profiles are included in the package, so the installed converter does not depend
on the checkout's `profiles/` directory.

## Prepare an offline installation

On a connected machine matching the intended offline machine's Python, operating
system and architecture, gather the reviewed project wheel and dependency wheels:

```bash
python -m pip download --only-binary=:all: --dest wheelhouse dist/verbatim_md-0.1.0-py3-none-any.whl
```

Copy `wheelhouse/` to the offline machine. Create its virtual environment, then:

```bash
python -m pip install --no-index --find-links wheelhouse verbatim-md==0.1.0
```

This convenient wheelhouse resolves dependencies within the package's supported
version constraints. To preserve the repository's exact reviewed development
versions, download all entries of `requirements-dev.lock` with `--require-hashes`
for the target platform and keep the reviewed project wheel alongside them:

```bash
python -m pip download --require-hashes --only-binary=:all: -r requirements-dev.lock --dest wheelhouse
```

An offline contributor can install those locked dependencies with `--no-index
--find-links wheelhouse --require-hashes -r requirements-dev.lock`, followed by
`pip install --no-build-isolation --no-deps -e .`. A wheelhouse is an installation
bundle with third-party distributions and their notices; reviewing or publishing
one is separate from publishing this project's own MIT source/wheel.
