# Contributor and agent instructions

Understand intent before implementing. Protect long-term maintainability and push
back on changes that weaken evidence integrity or overstate compatibility.

- Canonical quotations are immutable. Never paraphrase, normalize, trim, truncate,
  fabricate, silently repair, or rewrite evidence during parsing or formatting.
- Keep presentation spans separate from evidence text. Use Unicode code-point
  half-open offsets. Validate schema objects before rendering.
- Distinguish unverified evidence, author-declared source verification, internal
  text preservation, structural DOCX tests and interactive macro compatibility.
- Read `docs/MARKDOWN_SPEC.md`, `docs/ARCHITECTURE.md` and relevant tests before
  changing interfaces. Record consequential choices in ADRs.
- Run `pytest`, `ruff check src tests`, and `mypy src/verbatim_md`; validate and build
  all examples after parser, schema, profile or renderer changes. Add tests that
  prove behavior rather than merely reproduce implementation.
- Prefer focused modules and existing dependencies. Keep offline conversion and
  cross-platform paths. Reject malformed data with useful errors.
- For parallel work, assign disjoint ownership and agree on contracts before
  editing. Integrate continuously and independently verify critical deliverables.
  Never claim a subagent or test ran unless it actually did.
- Never incorporate upstream Verbatim source, macros or copyrighted templates
  without license review. Tutorial examples must be original, explicitly
  unverified text. Do not commit private evidence or generated build directories.
- Keep docs, examples and skills synchronized with actual implemented syntax.
  Do not publish packages, repositories or releases without authorization.
