# Reference templates

No Microsoft or Verbatim template is redistributed here. The renderer creates
macro-free DOCX packages and required style definitions itself.

You may provide a trusted local `.docx` through `--template reference.docx` if you
have permission to use it. Existing template body content is removed for the new
export. Required converter styles are configured deterministically. Macro-enabled
`.dotm`/`.docm` files, VBA parts and external relationships are rejected. This is
not a sandbox for hostile templates: use files from trusted sources only.

Keep copyrighted templates outside this repository. Consult the upstream Verbatim
license before redistributing any of its assets. A template does not establish
Word/Verbatim macro compatibility; run the manual matrix on your environment.
