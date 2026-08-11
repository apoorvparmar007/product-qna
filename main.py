from langchain.agents import create_agent
from langgraph.graph import StateGraph, START, END
from typing import TypedDict
from langchain_ollama import ChatOllama
# from langchain_community.tools import DuckDuckGoSearchResults
from langchain_core.tools import tool
import sqlite3
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from tools import check_product_availability,check_product_price

load_dotenv()



class ProductState(TypedDict):
    query: str
    product: str
    company: str



def chat_node(state: ProductState):
    # question = """do you have RC robot currently in stock?"""
    query = state['query']
    print("\n User Query: ",query,"\n")
    # llm = ChatOllama(model = 'qwen3:8b')
    llm = ChatGoogleGenerativeAI(model = 'gemini-3.1-flash-lite')

    agent = create_agent(
    model=llm,
    tools=[check_product_availability,check_product_price],
    system_prompt="You are a helpful assistant. Use tools when necessary. Answer the user question")

    input_data = {
    "messages": [
        {"role": "user", "content": query}
    ]}

    # for step in agent.stream(input_data, stream_mode="values"):
    #     last_message = step["messages"][-1]
    #     last_message.pretty_print()

    response = agent.invoke(input_data)

    print("\n Printing the response\n")
    content = response["messages"][-1].content
    text = content[0]["text"]

    print(text)

    return ({'product':text})

graph = StateGraph(ProductState)

graph.add_node("chat_node",chat_node)

graph.add_edge(START,"chat_node")
graph.add_edge("chat_node",END)

workflow = graph.compile()

# query = """what models of RC robot do you have?"""

user_input = input()

workflow.invoke({"query":user_input})

# for event in agent.stream(input_data, stream_mode="values"):
#     # This prints every step, state update, and LLM message as it happens
#     if "messages" in event:
#         last_message = event["messages"][-1]
#         print(f"[{last_message.type.upper()}]: {last_message.content}")