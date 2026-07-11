from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

from openrecall.build import build_dataset
from openrecall.validate import validate_dataset


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="openrecall")
    subparsers = parser.add_subparsers(dest="command", required=True)

    build_parser = subparsers.add_parser("build", help="Build static recall data")
    build_parser.add_argument("--output", type=Path, default=Path("data"))
    build_parser.add_argument("--config", type=Path, default=Path("openrecall.config.json"))
    build_parser.add_argument("--source", action="append", dest="sources")

    validate_parser = subparsers.add_parser("validate", help="Validate generated data")
    validate_parser.add_argument("root", type=Path)

    dist_parser = subparsers.add_parser("dist", help="Build deployable static directory")
    dist_parser.add_argument("--site", type=Path, default=Path("site"))
    dist_parser.add_argument("--data", type=Path, default=Path("data"))
    dist_parser.add_argument("--output", type=Path, default=Path("dist"))

    args = parser.parse_args(argv)
    if args.command == "build":
        metadata = build_dataset(args.output, sources=args.sources, config_path=args.config)
        print(f"Built {metadata['record_count']} records into {args.output}")
    elif args.command == "validate":
        errors = validate_dataset(args.root)
        if errors:
            for error in errors:
                print(error, file=sys.stderr)
            raise SystemExit(1)
        print(f"Validated {args.root}")
    elif args.command == "dist":
        build_dist(args.site, args.data, args.output)
        print(f"Built {args.output}")


def build_dist(site: Path, data: Path, output: Path) -> None:
    if output.exists():
        shutil.rmtree(output)
    shutil.copytree(site, output)
    shutil.copytree(data, output / "data")
