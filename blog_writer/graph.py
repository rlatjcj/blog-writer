"""Graph for blog writer."""

from langgraph.graph import StateGraph

from blog_writer.agents import create_outline_generator, create_writer
from blog_writer.utils import State, save_graph


def create_graph():
    """Create a graph for blog writing process."""
    workflow = StateGraph(State)

    # Add nodes
    workflow.add_node("outline_generator", create_outline_generator)
    workflow.add_node("writer", create_writer)

    # Add edges
    workflow.add_edge("outline_generator", "writer")

    # Set entry and exit points
    workflow.set_entry_point("outline_generator")
    workflow.set_finish_point("writer")

    # Compile graph
    compiled_graph = workflow.compile()

    save_graph(compiled_graph, "images/graph.png")

    return compiled_graph
