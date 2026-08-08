# Product QnA

A small ReAct-style agent, built with LangChain's `create_agent`, that answers questions using a local Ollama model and web search via DuckDuckGo.

## Requirements

- Python 3.10+ (LangChain's `create_agent` requires it)
- [Ollama](https://ollama.com) running locally with a tool-calling-capable model pulled (e.g. `qwen3:8b`, `qwen2.5`, `llama3.2`)
- Python packages: `langchain`, `langchain-ollama`, `langchain-community`, `langgraph`

## Setup

```bash
python3 -m venv .product
source .product/bin/activate
pip install langchain langchain-ollama langchain-community langgraph

ollama pull qwen3:8b
```

## Usage

```bash
python main.py
```

The agent is given a question, and can call the DuckDuckGo search tool when it needs up-to-date information to answer.

## Notes

- Not every Ollama model supports tool calling. Check a model's template for a `{{ if .Tools }}` block (`ollama show <model> --modelfile`) before relying on it to make tool calls.
