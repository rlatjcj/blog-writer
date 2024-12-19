from typing import Annotated, Sequence, TypedDict
from langgraph.graph import Graph, END
from langchain_core.messages import BaseMessage
from blog_writer.tools.writer import PostWriter, BlogPostInput
from blog_writer.tools.embedder import ReferenceEmbedder


class BlogState(TypedDict):
    title: str
    information: str
    images: list[str]
    reference: str
    retrieved_contents: list[str]
    blog_content: dict


def create_blog_workflow():
    embedder = ReferenceEmbedder()
    writer = PostWriter()

    def retrieve_references(state: BlogState) -> BlogState:
        embedder.set_reference_into_db(state["title"])
        retrieved_docs = embedder.retriever.get_relevant_documents(state["information"])
        state["retrieved_contents"] = [doc.page_content for doc in retrieved_docs]
        return state

    def write_blog(state: BlogState) -> BlogState:
        input_data = BlogPostInput(
            title=state["title"],
            information=state["information"],
            images=state["images"],
            reference=state["reference"],
            retrieved_contents=state["retrieved_contents"],
        )
        state["blog_content"] = writer.write_blog_post(input_data)
        return state

    # Define the graph
    workflow = Graph()

    # Add nodes
    workflow.add_node("retrieve_references", retrieve_references)
    workflow.add_node("write_blog", write_blog)

    # Add edges
    workflow.add_edge("retrieve_references", "write_blog")
    workflow.add_edge("write_blog", END)

    # Set entry point
    workflow.set_entry_point("retrieve_references")
    graph = workflow.compile()

    # Visualize and save the graph
    try:
        import cv2
        import numpy as np

        graph_image = graph.get_graph().draw_mermaid_png()
        # Convert bytes to numpy array
        nparr = np.frombuffer(graph_image, np.uint8)
        # Decode image
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        # Save image using cv2
        cv2.imwrite("images/blog_workflow.png", img)
    except Exception as e:
        print(f"Failed to save graph visualization: {e}")

    return graph
