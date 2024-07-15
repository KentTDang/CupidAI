from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated, List
import operator
from langgraph.checkpoint.sqlite import SqliteSaver
from langchain_core.messages import AnyMessage, SystemMessage, HumanMessage, AIMessage, ChatMessage
from langchain_openai import ChatOpenAI
from langchain_core.pydantic_v1 import BaseModel
from tavily import TavilyClient
import os
from flask import Flask, jsonify, request
from flask_cors import CORS


_ = load_dotenv()
memory = SqliteSaver.from_conn_string(":memory:")
tavily = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])
model = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

class Queries(BaseModel):
    queries: List[str]

PLAN_PROMPT = """You are an expert disaster response planner tasked with creating a comprehensive \
    response plan for a given disaster scenario. Write such an outline for the user provided \
    disaster scenario. Give an outline of the plan along with any relevant notes or instructions \
    for the disaster response plan.
"""

RESPONDER_PROMPT = """You are a disaster response assistant tasked with executing a comprehensive disaster response plan. \
Utilize the detailed plan provided by the planning agent to implement the response effectively. Your responsibilities include \
coordinating resources, managing communication, and adapting to evolving situations. If there are updates or critiques from \
the planning agent or response teams, adjust your actions accordingly. Utilize all the information below as needed:

------

{content}"""

REFLECTION_PROMPT = """You are a disaster response expert reviewing a disaster response plan. 
Generate critique and recommendations for the provided plan. 
Provide detailed recommendations, including requests for additional details, improvements in strategy, and suggestions for better resource management and communication.
Ensure your feedback is constructive and actionable.

------

{content}"""

RESEARCH_PLAN_PROMPT = """You are a researcher charged with providing information that can 
be used to enhance the following disaster response plan. Generate a list of search queries that will gather 
any relevant information. Only generate 3 queries max. 

------

{content}"""

RESEARCH_CRITIQUE_PROMPT = """You are a researcher charged with providing information that can 
be used to make any requested revisions to the disaster response plan (as outlined below). 
Generate a list of search queries that will gather any relevant information. Only generate 3 queries max. 

------

{content}"""

class AgentState(TypedDict):
    task: str
    plan: str
    draft: str
    critique: str
    content: List[str]
    revision_number: int
    max_revisions: int

def plan_node(state: AgentState):
    message = [ 
        SystemMessage(content=PLAN_PROMPT),
        HumanMessage(content=state['task'])
    ]
    response = model.invoke(message)
    return {'plan':response.content}

def research_plan_node(state: AgentState):
    queries = model.with_structured_output(Queries).invoke([
        SystemMessage(content=RESEARCH_PLAN_PROMPT),
        HumanMessage(content=state['task'])
    ])
    content = state['content'] or []
    for q in queries.queries:
        response = tavily.search(query=q, max_results=2)
        for r in response['results']:
            content.append(r['content'])
    return {"content": content}

def generation_node(state: AgentState):
    content = "\n\n".join(state['content'] or [])
    user_message = HumanMessage(
        content=f"{state['task']}\n\nHere is my plan:\n\n{state['plan']}")
    messages = [
        SystemMessage(
            content=REFLECTION_PROMPT.format(content=content)
        ),
        user_message
        ]
    response = model.invoke(messages)
    return {
        "draft": response.content, 
        "revision_number": state.get("revision_number", 1) + 1
    }

def reflection_node(state: AgentState):
    messages = [
        SystemMessage(content=REFLECTION_PROMPT), 
        HumanMessage(content=state['draft'])
    ]
    response = model.invoke(messages)
    return {"critique": response.content}

def research_critique_node(state: AgentState):
    queries = model.with_structured_output(Queries).invoke([
        SystemMessage(content=RESEARCH_CRITIQUE_PROMPT),
        HumanMessage(content=state['critique'])
    ])
    content = state['content'] or []
    for q in queries.queries:
        response = tavily.search(query=q, max_results=2)
        for r in response['results']:
            content.append(r['content'])
    return {"content": content}

def should_continue(state):
    if state["revision_number"] > state["max_revisions"]:
        return END
    return "reflect"

builder = StateGraph(AgentState)
builder.add_node("planner", plan_node)
builder.add_node("generate", generation_node)
builder.add_node("reflect", reflection_node)
builder.add_node("research_plan", research_plan_node)
builder.add_node("research_critique", research_critique_node)
builder.set_entry_point("planner")
builder.add_conditional_edges(
    "generate", 
    should_continue, 
    {END: END, "reflect": "reflect"}
)
builder.add_edge("planner", "research_plan")
builder.add_edge("research_plan", "generate")

builder.add_edge("reflect", "research_critique")
builder.add_edge("research_critique", "generate")
graph = builder.compile(checkpointer=memory)
thread = {"configurable": {"thread_id": "1"}}

app = Flask(__name__)
cors = CORS(app, origins='*')

print(graph.stream)

@app.route("/api/disaster-response", methods=['GET'])
def get_disaster_response():
    results = []
    for s in graph.stream({
        'task': "Floods and Landslides in Bangladesh",
        "max_revisions": 1,
        "revision_number": 1,
    }, thread):
        results.append(s)
    
    return jsonify(results)

if __name__ == "__main__":
    app.run(debug=True, port=8080)