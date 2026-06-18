"""Graph-visual builders for the SDK facade — Obsidian graph notes + interactive HTML.

Extracted from facade.py to keep every module within the 150-line limit. Pure
functions; the facade passes in the loaded graph + config and stays a thin
orchestrator.
"""

from __future__ import annotations

from typing import Any

from graphguide.graphify.centrality import hub_nodes
from graphguide.graphify.html_graph import build_interactive_html
from graphguide.vault_builder.graph_pages import generate as generate_graph_notes
from graphguide.vault_builder.graph_pages import select_nodes


def hub_and_suspects(
    graph: Any, hub_cfg: dict, suspect_nodes: set[str]
) -> tuple[set[str], set[str]]:
    hub = {
        x["node"]
        for x in hub_nodes(
            graph.to_networkx(),
            degree_warning=int(hub_cfg["degree_warning"]),
            degree_critical=int(hub_cfg["degree_critical"]),
            betweenness_warning=float(hub_cfg["betweenness_warning"]),
            betweenness_critical=float(hub_cfg["betweenness_critical"]),
        )
    }
    return hub, set(suspect_nodes)


def graph_vault(
    graph: Any, hub: set[str], suspects: set[str], nodes_dir: str, bug_node: str, vcfg: dict
) -> list[str]:
    return generate_graph_notes(
        graph,
        nodes_dir,
        bug_node=bug_node,
        top_n=int(vcfg["top_n"]),
        hops=int(vcfg["hops"]),
        cap=int(vcfg["max_notes"]),
        hub=hub,
        suspects=suspects,
    )


def html_graph(
    graph: Any, hub: set[str], suspects: set[str], out: str, bug_node: str, vcfg: dict
) -> str:
    selected = select_nodes(
        graph, bug_node, int(vcfg["top_n"]), int(vcfg["hops"]), int(vcfg["max_notes"])
    )
    return build_interactive_html(
        graph, out, selected=selected, hub=hub, suspects=suspects, bug_node=bug_node
    )
