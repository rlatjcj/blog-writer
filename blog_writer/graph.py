"""Graph for blog writer."""

from langgraph.graph import END, StateGraph

from blog_writer.agents import create_outline_generator, create_writer
from blog_writer.utils import State, save_graph


def create_graph():
    """Create a graph for blog writer."""
    graph = StateGraph(State)

    graph.add_node("outline_generator", create_outline_generator)
    # graph.add_node("supervisor", supervisor)
    # graph.add_node("reference_scrapper", reference_scrapper)
    graph.add_node("writer", create_writer)

    # graph.add_edge("outline_generator", "supervisor")
    # graph.add_edge("writer", "supervisor")
    graph.set_entry_point("outline_generator")
    graph.add_edge("outline_generator", "writer")
    graph.add_edge("writer", END)

    # graph.add_conditional_edges(
    #     "supervisor",
    #     should_continue_writing,
    #     {"write_section": "contents_writer", "finalize_report": "report_generator"},
    # )

    compiled_graph = graph.compile()

    save_graph(compiled_graph, "images/graph.png")

    return compiled_graph
