from langchain.agents import create_agent
from langgraph.graph import StateGraph, START, END
from typing import TypedDict
from langchain_ollama import ChatOllama
# from langchain_community.tools import DuckDuckGoSearchResults
from langchain_core.tools import tool
import sqlite3
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()

# ddg_tool = DuckDuckGoSearchResults()

# from langchain_core.tools import tool

@tool
def check_product_price(product_name: str) -> str:
    """Check price for a toy product by name.

    Args:
        product_name: The name of the toy product to look up for price.
    """
    conn = sqlite3.connect("database/toyshop.db")
    cur = conn.cursor()

    cur.execute("SELECT price FROM products WHERE name LIKE ?", (f"%{product_name}%",))
    count = cur.fetchall()

    conn.close()

    return (f"""Price of {product_name} is {count}""")


@tool
def check_product_availability(product_name: str) -> str:
    """Check availability for a toy product by name.

    Args:
        product_name: The name of the toy product to look up.
    """
    conn = sqlite3.connect("database/toyshop.db")
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM products WHERE name LIKE ?", (f"%{product_name}%",))
    count = cur.fetchall()

    conn.close()

    return (f"""Found {count} records""")
    

    # for row in rows:
    #     print(row)

    # 

class ProductState(TypedDict):
    query: str
    product: str
    company: str



def chat_node(state: ProductState):
    # question = """do you have RC robot currently in stock?"""
    query = state['query']
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

    for step in agent.stream(input_data, stream_mode="values"):
        last_message = step["messages"][-1]
        last_message.pretty_print()

    response = agent.invoke(input_data)

    print("\n Printing the response\n")
    print(response["messages"][-1].content)

    return ({'product':response["messages"][-1].content})

graph = StateGraph(ProductState)

graph.add_node("chat_node",chat_node)

graph.add_edge(START,"chat_node")
graph.add_edge("chat_node",END)

workflow = graph.compile()

query = """what models of RC robot do you have?"""

workflow.invoke({"query":query})

# for event in agent.stream(input_data, stream_mode="values"):
#     # This prints every step, state update, and LLM message as it happens
#     if "messages" in event:
#         last_message = event["messages"][-1]
#         print(f"[{last_message.type.upper()}]: {last_message.content}")