from langgraph.graph import StateGraph, END
from graphs.pos_state import PosState
from graphs.nodes.parent_node import parent_node
from graphs.nodes.memory_node import memory_node

  
graph = StateGraph(PosState)
graph.add_node("parent", parent_node)
graph.add_node("memory", memory_node)

graph.add_edge( "parent", "memory")
graph.add_edge("memory", END)
graph.set_entry_point("parent")

compiled = graph.compile()
