from langchain.agents import create_agent
from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from langchain_ollama import ChatOllama
# from langchain_community.tools import DuckDuckGoSearchResults
from langchain_core.tools import tool
import sqlite3
# from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from tools import check_product_availability,check_product_price
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph.message import add_messages
from langgraph.checkpoint.sqlite import SqliteSaver
from pydantic import BaseModel,Field

load_dotenv()



class ProductState(TypedDict):
    chatbot_message: Annotated[list[BaseMessage], add_messages]
    # query: str
    # product: str
    # price: str

class QueryDecompose(BaseModel):
    product: str = Field(description="Product name that user is asking about")
    price: str = Field(description="Is user asking about the price of the product?")
    stock_availability: str = Field(description="Is user asking about the availability of the Product?")

def query_node(state: ProductState):
    llm = ChatOllama(model = 'qwen3:8b')
    structured_model = llm.with_structured_output(QueryDecompose)

    query = state['query']

    response = structured_model.invoke(query)
    print (response)

def chat_node(state: ProductState):
    # question = """do you have RC robot currently in stock?"""
    query = state['chatbot_message']

    print("\n User Query: ",query,"\n")
    llm = ChatOllama(model = 'qwen3:8b')
    # structured_model = llm.with_structured_output(QueryDecompose)
    # llm = ChatGoogleGenerativeAI(model = 'gemini-3.1-flash-lite')

    agent = create_agent(
    model=llm,
    tools=[check_product_availability,check_product_price],
    system_prompt="You are a helpful assistant. Use tools when necessary. Answer the user question")

    input_data = {"messages": query}

    # for step in agent.stream(input_data, stream_mode="values"):
    #     last_message = step["messages"][-1]
    #     last_message.pretty_print()

    response = agent.invoke(input_data)

    print("\n Printing the response\n")
    content = response["messages"][-1].content
    # text = content[0]["text"]

    print(content)

    return {'chatbot_message':[content]}

conn = sqlite3.connect(database = "database/checkpoint.db",check_same_thread = False)
checkpointer = SqliteSaver(conn)

graph = StateGraph(ProductState)

graph.add_node("chat_node",chat_node)
graph.add_node("query_node",query_node)

graph.add_edge(START,"chat_node")
graph.add_edge("chat_node",END)

workflow = graph.compile(checkpointer=checkpointer)


def reterieve_all_threads():
    all_threads = set()
    for checkpoint in checkpointer.list(None):
        all_threads.add(checkpoint.config['configurable']['thread_id'])

    return list(all_threads)
# query = """what models of RC robot do you have?"""

# user_input = input()

# workflow.invoke({"query":user_input})

# for event in agent.stream(input_data, stream_mode="values"):
#     # This prints every step, state update, and LLM message as it happens
#     if "messages" in event:
#         last_message = event["messages"][-1]
#         print(f"[{last_message.type.upper()}]: {last_message.content}")