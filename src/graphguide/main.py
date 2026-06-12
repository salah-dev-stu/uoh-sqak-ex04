"""CLI entry (FR-CLI-001) — thin dispatch to the GraphGuide SDK façade."""

from __future__ import annotations

import argparse
import json

from graphguide.sdk.facade import GraphGuide


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="graphguide")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("version")
    sub.add_parser("graphify")
    sub.add_parser("vault")
    inv = sub.add_parser("investigate")
    inv.add_argument("--mode", choices=["graph", "naive"], default="graph")
    sub.add_parser("suspects")
    sub.add_parser("knowledge-diff")
    sub.add_parser("token-report")
    return parser


def main(argv: list[str] | None = None, gg: GraphGuide | None = None) -> int:
    args = build_parser().parse_args(argv)
    gg = gg or GraphGuide()
    if args.command == "version":
        print(gg.version())
    elif args.command == "graphify":
        print(gg.graphify())
    elif args.command == "vault":
        print(gg.build_vault())
    elif args.command == "investigate":
        print(json.dumps(gg.investigate(args.mode), indent=2))
    elif args.command == "suspects":
        print(json.dumps(gg.rank_suspects(), indent=2))
    elif args.command == "knowledge-diff":
        print(json.dumps(gg.knowledge_diff(), indent=2))
    elif args.command == "token-report":
        print(gg.token_report())
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
