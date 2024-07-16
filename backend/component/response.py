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
        self.PLAN_PROMPT = ("""You are an expert disaster response planner tasked with creating a comprehensive \
                            response plan for a given disaster scenario. Write such an outline for the user provided \
                            disaster scenario. Give an outline of the plan along with any relevant notes or instructions \
                            for the disaster response plan.
                            """)
        self.WRITER_PROMPT = ("""You are a disaster response assistant tasked with executing a comprehensive disaster response plan. \
                                Utilize the detailed plan provided by the planning agent to implement the response effectively. Your responsibilities include \
                            coordinating resources, managing communication, and adapting to evolving situations. If there are updates or critiques from \
                            the planning agent or response teams, adjust your actions accordingly. Utilize all the information below as needed:

                            ------

                            """)

        self.REFLECTION_PROMPT = ("""You are a disaster response expert reviewing a disaster response plan. 
                            Generate critique and recommendations for the provided plan. 
                            Provide detailed recommendations, including requests for additional details, improvements in strategy, and suggestions for better resource management and communication.
                            Ensure your feedback is constructive and actionable.

                            ------

                            """)

        self.RESEARCH_PLAN_PROMPT = ("""You are a researcher charged with providing information that can 
                            be used to enhance the following disaster response plan. Generate a list of search queries that will gather 
                            any relevant information. Only generate 3 queries max. 

                            ------

                            """)

        self.RESEARCH_CRITIQUE_PROMPT = ("""You are a researcher charged with providing information that can 
                            be used to make any requested revisions to the disaster response plan (as outlined below). 
                            Generate a list of search queries that will gather any relevant information. Only generate 3 queries max. 

                            ------

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
            interrupt_after=['planner', 'generate', 'reflect', 'research_plan', 'research_critique']
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
        content = state['content'] or [] # add to content
        for q in queries.queries:
            response = self.tavily.search(query = q, max_result = 2)
            for r in response['result']:
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
        content = state['content'] or []
        for q in queries.queries:
            response = self.tavily.search(query = q, max_results = 2)
            for r in response['results']:
                content.append(r['content'])
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

@app.route("/api/disaster-response", methods=['GET'])
def get_disaster_response():
    result = []
    for s in response_instance.graph.stream({
    'task': "Hurricane Beryl ",
    "max_revisions": 2,
    "revision_number": 1,
    }, thread):
        print(s)
        result.append(s)

    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True, port=8080)
