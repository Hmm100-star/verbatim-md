# Formatting and profiles

Formatting references canonical evidence code points using independent half-open
ranges. A run is split at each span boundary. Overlapping highlight, underline,
emphasis and small text therefore apply to exactly the same characters without
editing them. Newlines remain canonical newlines when mapped to DOCX paragraphs.

`highlight` applies a Word highlight color; `underline` applies single underline;
`emphasis` applies bold and underline; `small` uses the configured small size. No state carries
from one card to the next. Citation spans additionally support `cite`, Verbatim's
citation character style. Word styles supply hierarchy and body defaults; direct
run formatting represents only the requested character-level annotations.

Run `verbatim-md profiles list` to inspect built-in `default` and `ld` profiles.
A custom YAML profile supports these fields:

```yaml
font_name: Arial
font_size: 11
small_size: 8
highlight_color: yellow
shrink_unread: false
margin_inches: 1
```

`shrink_unread: true` shrinks evidence outside underlined or emphasized ranges,
following the documented Verbatim Shrink selection rule. Highlight alone does
not protect a range from shrinking. Explicit `small` spans always use the small
size, including on underlined or highlighted text. Otherwise evidence uses the
normal body size. No quotation text
is deleted by shrinking. Font sizes use half-point increments (11 or 11.5); unsupported fractions are
rejected instead of silently rounded. Sizes are points; margins are inches. Supported highlight
colors: yellow, green, cyan, magenta, blue, red, darkYellow and lightGray. Unknown
keys, nonfinite/out-of-range sizes and small sizes above body size fail validation.

Profile selection is explicit (`--profile ld` or `--profile profile.yaml`), so files
cannot automatically load arbitrary local configuration. Fonts must be installed
in the viewer; substitution may change pagination. Visual similarity does not
prove macro compatibility; consult the compatibility matrix.
