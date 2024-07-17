from langgraph.graph import StateGraph, END
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.sqlite import SqliteSaver
from tavily import TavilyClient
import sqlite3
from models import AgentState, Queries
import config

class DatePlanner:
    def __init__(self):
        self.model = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
        self.tavily = TavilyClient(api_key=config.TAVILY_API_KEY)
        self._define_prompts()
        self._build_state_graph()

    def _define_prompts(self):
        self.PLAN_PROMPT = """You are an expert date planner tasked with creating a comprehensive, interesting, and enjoyable date plan for a given prompt..."""
        self.WRITER_PROMPT = """You are an expert date planner assistant tasked with writing a detailed date plan..."""
        self.RESEARCH_PLAN_PROMPT = """You are an expert researcher tasked with providing information to enhance the following date plan..."""
        self.REFLECTION_PROMPT = """You are an expert date planner reviewing a date plan..."""
        self.RESEARCH_CRITIQUE_PROMPT = """You are an expert researcher tasked with providing information that can be used for making any requested revisions..."""

    def _build_state_graph(self):
        builder = StateGraph(AgentState)
        builder.add_node("planner", self.plan_node)
        builder.add_node("research_plan", self.research_plan_node)
        builder.add_node("generate", self.generation_node)
        builder.add_node("reflect", self.reflection_node)
        builder.add_node("research_critique", self.research_critique_node)
        builder.set_entry_point("planner")
        builder.add_conditional_edges("generate", self.should_continue, {END: END, "reflect": "reflect"})
        builder.add_edge("planner", "research_plan")
        builder.add_edge("research_plan", "generate")
        builder.add_edge("reflect", "research_critique")
        builder.add_edge("research_critique", "generate")
        memory = SqliteSaver(conn=sqlite3.connect(":memory:", check_same_thread=False))
        self.graph = builder.compile(checkpointer=memory)

    def plan_node(self, state: AgentState):
        messages = [SystemMessage(content=self.PLAN_PROMPT), HumanMessage(content=state['task'])]
        response = self.model.invoke(messages)
        return {"plan": response.content, "lnode": "planner", "count": 1}

    def research_plan_node(self, state: AgentState):
        queries = self.model.with_structured_output(Queries).invoke([
            SystemMessage(content=self.RESEARCH_PLAN_PROMPT),
            HumanMessage(content=state['task'])
        ])
        content = []
        for q in queries.queries:
            response = self.tavily.search(query=q, max_results=2)
            for r in response['results']:
                content.append(r['content'])
        return {"content": content, "queries": queries.queries, "lnode": "research_plan", "count": 1}

    def generation_node(self, state: AgentState):
        content = "\n\n".join(state['content'] or [])
        user_message = HumanMessage(content=f"{state['task']}\n\nHere is my plan:\n\n{state['plan']}")
        messages = [SystemMessage(content=self.WRITER_PROMPT.format(content=content)), user_message]
        response = self.model.invoke(messages)
        return {"draft": response.content, "revision_number": state.get("revision_number", 1) + 1, "lnode": "generate", "count": 1}

    def reflection_node(self, state: AgentState):
        messages = [SystemMessage(content=self.REFLECTION_PROMPT), HumanMessage(content=state['draft'])]
        response = self.model.invoke(messages)
        return {"critique": response.content, "lnode": "reflect", "count": 1}

    def research_critique_node(self, state: AgentState):
        queries = self.model.with_structured_output(Queries).invoke([
            SystemMessage(content=self.RESEARCH_CRITIQUE_PROMPT),
            HumanMessage(content=state['critique'])
        ])
        content = []
        for q in queries.queries:
            response = self.tavily.search(query=q, max_results=2)
            for r in response['results']:
                content.append(r['content'])
        queries.queries.clear()
        return {"content": content, "lnode": "research_critique", "count": 1}

    def should_continue(self, state):
        if state['revision_number'] > state['max_revisions']:
            return END
        return "reflect"
