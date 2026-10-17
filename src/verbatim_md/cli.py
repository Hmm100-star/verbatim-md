"""Command-line interface; all conversion remains local."""
import argparse
from dataclasses import asdict
import json
from pathlib import Path
import sys

from .config import BUILTINS, load_profile


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="verbatim-md", description=__doc__)
    parser.add_argument("--version", action="version", version="verbatim-md 0.1.0")
    parser.add_argument("--verbose", action="store_true", help="include diagnostic details")
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("build", "validate", "inspect", "build-all"):
        command = sub.add_parser(name)
        command.add_argument("input", type=Path)
        command.add_argument("--json", action="store_true", help="machine-readable report")
        if name in ("build", "build-all"):
            command.add_argument("--profile", help="default, ld, or a YAML path")
            command.add_argument("--strict", action="store_true", help="fail on validation warnings")
            command.add_argument("--force", action="store_true", help="replace existing output")
            command.add_argument("--template", type=Path, help="optional trusted local reference DOCX")
            command.add_argument("-o" if name == "build" else "--out", required=True, type=Path)
        elif name == "inspect":
            command.add_argument("--against", type=Path, help="compare DOCX with canonical Markdown after Word editing")
        elif name == "validate":
            command.add_argument("--strict", action="store_true", help="fail on validation warnings")
    profiles = sub.add_parser("profiles")
    profiles.add_argument("action", choices=["list"])
    profiles.add_argument("--json", action="store_true")
    return parser


def _emit(report: dict, machine: bool) -> None:
    if machine:
        print(json.dumps(report, ensure_ascii=False, indent=2, default=str))
    else:
        print(json.dumps(report, ensure_ascii=False, indent=2, default=str))


def _successful(report: dict, strict: bool = False) -> bool:
    if (report.get("valid") is False or report.get("ok") is False
            or report.get("internally_preserved") is False or report.get("errors")):
        return False
    return not (strict and report.get("warnings"))


def main(argv: list[str] | None = None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)
    report: dict
    try:
        from .api import build, inspect_file, validate_file
        if args.command == "profiles":
            report = {"profiles": {key: asdict(value) for key, value in BUILTINS.items()}}
        elif args.command == "validate":
            report = validate_file(args.input)
        elif args.command == "inspect":
            if args.against is not None:
                from .api import parse_file, verify_against_document
                report = verify_against_document(parse_file(args.against), args.input)
            else:
                report = inspect_file(args.input)
        elif args.command == "build":
            load_profile(args.profile)
            validation = validate_file(args.input)
            if not _successful(validation, args.strict):
                _emit(validation, args.json)
                return 1
            report = build(args.input, args.o, profile=args.profile,
                           overwrite=args.force, template=args.template)
        else:
            load_profile(args.profile)
            root = args.input.resolve()
            destination = args.out.resolve()
            if not root.is_dir():
                raise ValueError("build-all input must be a directory")
            if destination == root or root in destination.parents:
                raise ValueError("batch output must be outside the input directory")
            paths = sorted(root.rglob("*.md"))
            if not paths:
                raise ValueError("no .md files found")
            results = []
            for path in paths:
                try:
                    validation = validate_file(path)
                    if not _successful(validation, args.strict):
                        results.append({"input": str(path), "ok": False, "validation": validation})
                        continue
                    output = destination / path.relative_to(root).with_suffix(".docx")
                    if not output.resolve().is_relative_to(destination):
                        raise ValueError('batch destination symlink escapes output directory')
                    for parent in output.parents:
                        if parent == destination:
                            break
                        if parent.is_symlink():
                            raise ValueError('batch destination contains a symlink directory')
                    output.parent.mkdir(parents=True, exist_ok=True)
                    result = build(path, output, profile=args.profile,
                                   overwrite=args.force, template=args.template)
                    results.append({"input": str(path), "ok": True, "result": result})
                except (ValueError, OSError) as exc:
                    results.append({"input": str(path), "ok": False, "error": str(exc)})
            report = {"ok": all(item["ok"] for item in results), "results": results}
        _emit(report, args.json)
        return 0 if _successful(report, getattr(args, "strict", False)) else 1
    except (ValueError, OSError) as exc:
        report = {"ok": False, "error": str(exc), "error_type": type(exc).__name__}
        if getattr(args, "json", False):
            _emit(report, True)
        else:
            print(f"verbatim-md: {exc}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc(file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
