# ADR 1 Separate evidence from formatting

Accepted. Canonical LF text is immutable and formatting uses half-open Python Unicode code-point offsets. Literal fences perform no Markdown, HTML, escape, whitespace or Unicode normalization. Crossed and nested spans are equivalent sets of active attributes. Reject invalid bounds and XML-invalid characters instead of fixing them. This requires authors to compute offsets, but avoids ambiguous inline marker removal and protects quotation integrity.
