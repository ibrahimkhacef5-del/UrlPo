#!/usr/bin/env python3
"""CLI for urlpo."""

import argparse
import sys
from pathlib import Path

from urlpo.core import process_file


def main():
    p = argparse.ArgumentParser(
        prog="urlpo",
        description="Extract all links from HTML/JS/CSS and download them into UrlPo/",
    )
    p.add_argument("file", help="Path to .html / .js / .css file")
    p.add_argument(
        "-o", "--out",
        default="UrlPo",
        help="Output folder (default: UrlPo)",
    )
    p.add_argument(
        "-b", "--base",
        default=None,
        help="Base URL for resolving relative links",
    )
    p.add_argument(
        "-w", "--workers",
        type=int,
        default=8,
        help="Parallel download workers (default: 8)",
    )
    args = p.parse_args()

    try:
        res = process_file(args.file, out_dir=args.out, base_url=args.base, workers=args.workers)
        print(f"Done → {res['ok']} downloaded, {res['fail']} failed (total {res['total']})")
        print(f"Folder: {Path(args.out).resolve()}")
        sys.exit(0 if res["fail"] == 0 else 1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
