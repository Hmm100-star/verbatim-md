# ADR 3 Verify before atomic publication

Accepted. Write a temporary sibling DOCX; compare extracted evidence with immutable input; publish atomically with no-clobber semantics unless overwrite was explicitly requested. Deterministic ZIP ordering, timestamps and document properties support reproducibility. A JSON manifest aids later corruption detection; it does not authenticate adversarial edits or source accuracy. Word may discard this custom part: retain Markdown for independent comparisons after interactive edits.
