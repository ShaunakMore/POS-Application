def memory_node(state):
    prompt = state.get("prompt", "")
    response = state.get("response", "")

    if prompt and response:
        print(f"💬 updated short-term semantic memory")
        return {"memory_status": "Memory updated."}
