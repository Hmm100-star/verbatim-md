# Licensing review

Reviewed 2026-10-17. This is an engineering inventory, not a legal opinion.

## Distribution boundary

The converter's original code and original sample text may use MIT. This project must not include Verbatim VBA, `Debate.dotm`, installers, copyrighted debate evidence, or extracted upstream template assets under its MIT license. Compatibility facts and independently implemented OOXML styles are the intended integration boundary. Verbatim is a separate product; no endorsement is implied.

The [official Paperless Debate manual](https://docs.paperlessdebate.com/) identifies Verbatim as GPL3. Reading its documentation to establish interoperability does not authorize relicensing its implementation. Any future incorporation of GPL material requires a fresh license review and appropriate licensing; an MIT header cannot remove upstream obligations. User-supplied templates remain the user's responsibility and are not project assets.

## Runtime dependency inventory

| Component | Upstream license evidence | Distribution handling |
| --- | --- | --- |
| python-docx | [MIT license](https://github.com/python-openxml/python-docx/blob/master/LICENSE) | Install as dependency; retain upstream notices if vendoring or bundling it. |
| PyYAML | [MIT license](https://github.com/yaml/pyyaml/blob/main/LICENSE) | Install as dependency; retain upstream notices if bundling it. |
| defusedxml | [Python Software Foundation license](https://github.com/tiran/defusedxml/blob/main/LICENSE) | Installed separately; retain PSF notices if bundled. |
| lxml, transitively used by python-docx | [Upstream licensing section](https://lxml.de/#license) | BSD-style lxml license; review bundled libxml2/libxslt notices for binary redistribution. |
| typing_extensions, transitively used by python-docx | [Python typing_extensions license](https://github.com/python/typing_extensions/blob/main/LICENSE) | Preserve Python Software Foundation license notices if bundled. |

Normal source/wheel publication of this project's original code does not relicense its separately installed dependencies. A frozen executable, offline wheelhouse, container image, or vendored distribution needs its own complete dependency notice inventory. Dev dependencies and GitHub Actions are not incorporated into the converter's source merely by running them, but their own distributions retain their licenses.

## Samples and release checks

Use original demonstrative text or clearly identified public-domain material. Do not assume an accessible news article, caselist card, or school case is licensed for redistribution. Record source and license for every future third-party fixture. Keep real debate evidence outside the converter repository. The user's attached brief is reference input and must not be packaged.

Before publishing: inspect both wheel and source archive; confirm no private evidence, downloaded Verbatim artifacts, credentials, local paths, or unrelated files; verify LICENSE is present; review dependency versions and vulnerabilities; preserve notices if adding vendored material. Public publication and package-name availability are separate release actions.
