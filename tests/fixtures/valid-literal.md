---
version: 1
title: Literal fixture
sources:
  - id: demo
    citation: "Original test text, Verbatim-MD contributors 2026"
---
# Pocket
## Hat
### Block
#### Unicode and overlap
:::card
id: literal
source: demo
spans:
  - {start: 0, end: 5, kind: highlight}
  - {start: 2, end: 8, kind: underline}
```text
A😀 café
Second paragraph.

Final line [hl]literal[/hl].
```
:::
