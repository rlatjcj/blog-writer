"""Graph for blog writer."""

from langgraph.graph import StateGraph

from blog_writer.agents import create_outline_generator, create_writer
from blog_writer.utils import State, save_graph


def create_graph():
    """Create a graph for blog writer."""
    graph = StateGraph(State)

    # Add nodes
    graph.add_node("outline_generator", create_outline_generator)
    graph.add_node("writer", create_writer)

    # Add edges
    graph.set_entry_point("outline_generator")
    graph.add_edge("outline_generator", "writer")
    graph.set_finish_point("writer")

    # Compile graph
    compiled_graph = graph.compile()

    save_graph(compiled_graph, "images/graph.png")

    return compiled_graph
