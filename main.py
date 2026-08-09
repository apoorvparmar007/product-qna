from langchain.agents import create_agent
from langgraph.graph import StateGraph, START, END
from typing import TypedDict
from langchain_ollama import ChatOllama
from langchain_community.tools import DuckDuckGoSearchResults
from langchain_core.tools import tool

ddg_tool = DuckDuckGoSearchResults()

class ProductState(TypedDict):
    query: str
    company: str


llm = ChatOllama(model = 'qwen3:8b')

prompt = "do you think it is right for U.S. military to  capture Venezuelan President Nicolás Maduro as they did in January 2026.?"


# Compile the agent loop
agent = create_agent(
    model=llm,
    tools=[ddg_tool],
    system_prompt="You are a helpful assistant. Use tools when necessary."

    # You can add custom middleware or prompt instructions here
)

input_data = {
    "messages": [
        {"role": "user", "content": prompt}
    ]
}
# agent_executor = AgentExecutor.invoke(agent=agent,tools=tool,verbose=True)
# response = agent.invoke(input_data)
# print(response["messages"][-1].content)


for event in agent.stream(input_data, stream_mode="values"):
    # This prints every step, state update, and LLM message as it happens
    if "messages" in event:
        last_message = event["messages"][-1]
        print(f"[{last_message.type.upper()}]: {last_message.content}")