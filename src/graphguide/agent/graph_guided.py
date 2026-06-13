"""Graph-guided investigator (FR-AGENT-001/002/004/005) — a LangGraph StateGraph.

Order is enforced by edges: index -> hot -> query_graph -> read_code -> diagnose,
then a bounded conditional loop to propose_fix. Raw code is read only after the
graph/vault have narrowed the suspects.
"""

from __future__ import annotations

from functools import partial

from langgraph.graph import END, StateGraph

from graphguide.agent import nodes
from graphguide.agent.context import AgentContext
from graphguide.agent.state import AgentState, initial_state


def build_graph(ctx: AgentContext):
    graph = StateGraph(AgentState)
    graph.add_node("read_index", partial(nodes.read_index, ctx))
    graph.add_node("read_hot", partial(nodes.read_hot, ctx))
    graph.add_node("query_graph", partial(nodes.query_graph, ctx))
    graph.add_node("read_code", partial(nodes.read_code, ctx))
    graph.add_node("diagnose", partial(nodes.diagnose, ctx))
    graph.add_node("expand", partial(nodes.expand, ctx))
    graph.add_node("propose_fix", partial(nodes.propose_fix, ctx))

    graph.set_entry_point("read_index")
    graph.add_edge("read_index", "read_hot")
    graph.add_edge("read_hot", "query_graph")
    graph.add_edge("query_graph", "read_code")
    graph.add_edge("read_code", "diagnose")
    graph.add_conditional_edges(
        "diagnose",
        partial(nodes.route_after_diagnose, ctx),
        {"propose_fix": "propose_fix", "expand": "expand"},
    )
    graph.add_edge("expand", "query_graph")  # frontier-expansion loop
    graph.add_edge("propose_fix", END)
    return graph.compile()


def run_graph_guided(ctx: AgentContext, task: str) -> AgentState:
    app = build_graph(ctx)
    return app.invoke(initial_state(task, "graph"))
