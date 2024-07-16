from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Annotated
from langgraph.checkpoint.sqlite import SqliteSaver
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langchain_core.pydantic_v1 import BaseModel
from tavily import TavilyClient
import os
from flask import Flask, jsonify, request
from flask_cors import CORS
import operator
import sqlite3
import uuid
import json


# Initialize dotenv to load environment variables
_ = load_dotenv()

# Configure a uuid for each conversation
thread = {"configurable": {"thread_id": uuid.uuid4()}}
class AgentState(TypedDict):
    task: str
    lnode: str
    plan: str
    draft: str
    critique: str
    content: List[str]
    queries: List[str]
    revision_number: int
    max_revisions: int
    count: Annotated[int, operator.add]
class Queries(BaseModel):
    queries: List[str]

class eresponse():
    def __init__(self):
        self.model = ChatOpenAI(model = "gpt-3.5-turbo", temperature=0)
        self.PLAN_PROMPT = ("""You are an expert date planner tasked with creating a comprehensive, interesting, \
                            and enjoyable date plan for a given prompt. Write such an outline for the user-provided \
                            prompt, keeping in mind their current location, time, and preferences. \
                            Provide an outline of the date plan along with any relevant notes or instructions \
                            for the activities.
                            """)
        
        self.WRITER_PROMPT = ("""You are an expert date planner assistant tasked with writing a detailed date plan. \
                              Generate the best date plan possible for the user’s request and the initial outline. \
                              If the user provides critique, respond with a revised version of your previous attempts. \
                              Utilize all the information below as needed:
                            ------
                            {content}
                            """)
        
        self.RESEARCH_PLAN_PROMPT = ("""You are an expert researcher tasked with providing information \
                                     to enhance the following date plan. Generate a list of search \
                                     queries to gather relevant information, including but not limited \
                                     to popular restaurants and activities based on social media and internet \
                                     sources. Generate a maximum of 3 queries.
                            """)

        self.REFLECTION_PROMPT = ("""You are an expert date planner reviewing a date plan. \
                                  Generate critique and recommendations for the user’s submission.
                            """)

        self.RESEARCH_CRITIQUE_PROMPT = ("""You are an expert researcher tasked with providing information \
                                         that can be used for making any requested revisions (as outlined below).\
                                        Generate a list of search queries to gather relevant information. \
                                         Only generate a maximum of 2 queries.
                            """)
        
        self.tavily = TavilyClient(api_key = os.environ["TAVILY_API_KEY"])
        builder = StateGraph(AgentState)
        builder.add_node("planner", self.plan_node)
        builder.add_node("research_plan", self.research_plan_node)
        builder.add_node("generate", self.generation_node)
        builder.add_node("reflect", self.reflection_node)
        builder.add_node("research_critique", self.research_critique_node)
        builder.set_entry_point("planner")
        builder.add_conditional_edges(
            "generate", 
            self.should_continue, 
            {END: END, "reflect": "reflect"}
        )
        builder.add_edge("planner", "research_plan")
        builder.add_edge("research_plan", "generate")
        builder.add_edge("reflect", "research_critique")
        builder.add_edge("research_critique", "generate")
        memory = SqliteSaver(conn=sqlite3.connect(":memory:", check_same_thread = False))
        self.graph = builder.compile(
            checkpointer = memory,
            # interrupt_after=['planner', 'generate', 'reflect', 'research_plan', 'research_critique']
        )
        
    def plan_node(self, state: AgentState):
        messages = [
            SystemMessage(content = self.PLAN_PROMPT),
            HumanMessage(content = state['task'])
        ]
        response = self.model.invoke(messages)
        return {"plan": response.content,
                "lnode": "planner",
                "count": 1,
        }
    
    def research_plan_node(self, state: AgentState):
        queries = self.model.with_structured_output(Queries).invoke([
            SystemMessage(content = self.RESEARCH_PLAN_PROMPT),
            HumanMessage(content = state['task'])
        ])
        content = [] # add to content
        for q in queries.queries:
            response = self.tavily.search(query=q, max_results=2)
            for r in response['results']:
                content.append(r['content'])
        return {"content": content,
                "queries": queries.queries,
                "lnode": "research_plan",
                "count": 1,
        }
    
    def generation_node(self, state: AgentState):
        content = "\n\n".join(state['content'] or [])
        user_message = HumanMessage(
            content=f"{state['task']}\n\nHere is my plan:\n\n{state['plan']}")
        messages = [
            SystemMessage(
                content=self.WRITER_PROMPT.format(content = content)
            ),
            user_message
        ]
        response = self.model.invoke(messages)
        return {"draft": response.content,
                "revision_number": state.get("revision_number", 1) + 1,
                "lnode": "generate",
                "count": 1,
        }
    
    def reflection_node(self, state: AgentState):
        messages = [
            SystemMessage(content = self.REFLECTION_PROMPT),
            HumanMessage(content = state['draft'])
        ]
        response = self.model.invoke(messages)
        return {"critique": response.content,
                "lnode": "reflect",
                "count": 1,
        }
    
    def research_critique_node(self, state: AgentState):
        queries = self.model.with_structured_output(Queries).invoke([
            SystemMessage(content = self.RESEARCH_CRITIQUE_PROMPT),
            HumanMessage(content = state['critique'])
        ])
        content = []
        for q in queries.queries:
            response = self.tavily.search(query=q, max_results=2)
            for r in response['results']:
                content.append(r['content'])
        queries.queries.clear()
        return {"content": content,
                "lnode": "research_critique",
                "count": 1,
        }

    def should_continue(self, state):
        if state['revision_number'] > state['max_revisions']:
            return END
        return "reflect" 


app = Flask(__name__)
cors = CORS(app, origins='*')   

response_instance = eresponse()

@app.route("/api/disaster-response", methods=['GET', 'POST'])
def get_disaster_response():
    task = 'Generate a date plan in Maryland'

    print(request.data)
    if request.method == 'POST':
        input = request.data.decode('utf-8')
        task = json.loads(input)["task"]

    result = []
    for s in response_instance.graph.stream({
    'task': task,
    'max_revisions': 2,
    'revision_number': 1,
    }, thread):
        print(s)
        result.append(s)

    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True, port=8080)
