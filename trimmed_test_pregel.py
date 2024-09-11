import pytest
from langgraph.graph import Graph, StateGraph, END, START
from langgraph.errors import InvalidUpdateError

# Define a simple logic function
def logic(inp: str) -> str:
    return ""

# Create a basic graph
def test_graph_validation() -> None:
    workflow = Graph()
    workflow.add_node("agent", logic)
    workflow.set_entry_point("agent")
    workflow.set_finish_point("agent")
    assert workflow.compile(), "valid graph"

    # Accept a dead-end
    workflow = Graph()
    workflow.add_node("agent", logic)
    workflow.set_entry_point("agent")
    workflow.compile()

    # Test unreachable finish point
    workflow = Graph()
    workflow.add_node("agent", logic)
    workflow.set_finish_point("agent")
    with pytest.raises(ValueError, match="not reachable"):
        workflow.compile()

    # Test conditional edges
    workflow = Graph()
    workflow.add_node("agent", logic)
    workflow.add_node("tools", logic)
    workflow.set_entry_point("agent")
    workflow.add_conditional_edges("agent", logic, {"continue": "tools", "exit": END})
    workflow.add_edge("tools", "agent")
    assert workflow.compile(), "valid graph"

    # Test invalid conditional edges
    workflow = Graph()
    workflow.set_entry_point("tools")
    workflow.add_conditional_edges("agent", logic, {"continue": "tools", "exit": END, "hmm": "extra"})
    workflow.add_edge("tools", "agent")
    workflow.add_node("agent", logic)
    workflow.add_node("tools", logic)
    with pytest.raises(ValueError, match="unknown"):  # extra is not defined
        workflow.compile()

    # Test unreachable node
    workflow = Graph()
    workflow.add_node("agent", logic)
    workflow.add_node("tools", logic)
    workflow.add_node("extra", logic)
    workflow.set_entry_point("agent")
    workflow.add_conditional_edges("agent", logic, {"continue": "tools", "exit": END})
    workflow.add_edge("tools", "agent")
    with pytest.raises(ValueError, match="Node `extra` is not reachable"):  # extra is not reachable
        workflow.compile()

# Define a state and a node function
class State(TypedDict):
    hello: str

def node_a(state: State) -> State:
    return {"hello": "world"}

# Create a state graph
def test_state_graph() -> None:
    builder = StateGraph(State)
    builder.add_node("a", node_a)
    builder.set_entry_point("a")
    builder.set_finish_point("a")
    graph = builder.compile()
    with pytest.raises(InvalidUpdateError):
        graph.invoke({"hello": "there"})

    # Test invalid edge
    graph = StateGraph(State)
    graph.add_node("start", lambda x: x)
    graph.add_edge("__start__", "start")
    graph.add_edge("unknown", "start")
    graph.add_edge("start", "__end__")
    with pytest.raises(ValueError, match="Found edge starting at unknown node "):
        graph.compile()

# Run the tests
if __name__ == "__main__":
    test_graph_validation()
    test_state_graph()
