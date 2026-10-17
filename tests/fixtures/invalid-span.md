---
version: 1
title: Invalid span
sources:
  - id: demo
    citation: Test
---
# Pocket
## Hat
### Block
#### Tag
:::card
id: card
source: demo
spans: [{start: 0, end: 999, kind: highlight}]
```text
Short quotation.
```
:::
