"""Visualize the review graph using IPython.display

For use in Jupyter notebooks, you can simply run:
    from IPython.display import Image, display
    from src.graph.review_graph import create_review_graph
    
    graph_builder = create_review_graph()
    display(Image(graph_builder.get_graph().draw_mermaid_png()))
"""

from src.graph.review_graph import create_review_graph

# Create the graph
graph_builder = create_review_graph()

# Try to use IPython.display if available (for Jupyter notebooks)
try:
    from IPython.display import Image, display
    # Display the graph as PNG in Jupyter
    display(Image(graph_builder.get_graph().draw_mermaid_png()))
except ImportError:
    # Fallback: save to file if not in Jupyter
    print("IPython not available. Saving PNG to graph_diagram.png instead...")
    png_bytes = graph_builder.get_graph().draw_mermaid_png()
    with open("graph_diagram.png", "wb") as f:
        f.write(png_bytes)
    print("Graph diagram saved to graph_diagram.png")
except Exception as e:
    print(f"Error displaying graph: {e}")
    # Fallback: save to file
    png_bytes = graph_builder.get_graph().draw_mermaid_png()
    with open("graph_diagram.png", "wb") as f:
        f.write(png_bytes)
    print("Graph diagram saved to graph_diagram.png")

