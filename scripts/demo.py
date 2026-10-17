"""Run Markdown -> validation -> export -> text/style verification, offline."""
import argparse
import json
from pathlib import Path

from verbatim_md import build, parse_file, validate_file, verify_against_document
from verbatim_md.compatibility import compatibility_report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, default=Path('artifacts/demo'))
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    args.out.mkdir(parents=True, exist_ok=True)
    results = []
    for source in sorted((root / 'examples').glob('*.md')):
        output = args.out / source.with_suffix('.docx').name
        validation = validate_file(source)
        build(source, output, overwrite=True)
        integrity = verify_against_document(parse_file(source), output)
        compatibility = compatibility_report(output)
        if not integrity['internally_preserved'] or not compatibility['structural_styles_present']:
            raise RuntimeError(f'Failed verification: {source.name}')
        results.append({'input': source.name, 'output': output.name,
                        'validation': validation, 'integrity': integrity,
                        'compatibility': compatibility})
    report = {'ok': True, 'results': results}
    (args.out / 'report.json').write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
