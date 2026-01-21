from langchain_community.tools import DuckDuckGoSearchRun

search_tool = DuckDuckGoSearchRun()

def gather_context(state):
    topic = state["topic"]
    objectives = state["objectives"]

    query = f"{topic} fundamentals explanation concepts"

    search_results = search_tool.run(query)

    state["context"] = search_results
    return state
