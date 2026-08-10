# Product QnA

A LangGraph agent that answers questions about toy shop inventory — product availability and pricing — by querying a local SQLite database. Built with LangChain's `create_agent` and Google's Gemini model.

## Requirements

- Python 3.10+ (LangChain's `create_agent` requires it)
- A Google AI API key (for `gemini-3.1-flash-lite` via `langchain-google-genai`)
- A `database/toyshop.db` SQLite file with a `products` table (columns include at least `name` and `price`)
- Python packages: `langchain`, `langchain-google-genai`, `langgraph`, `python-dotenv`

## Setup

```bash
python3 -m venv .product
source .product/bin/activate
pip install langchain langchain-google-genai langgraph python-dotenv
```

Create a `.env` file in the project root with your Google API key:

```
GOOGLE_API_KEY=your-key-here
```

## Usage

```bash
python main.py
```

The script builds a single-node LangGraph workflow (`chat_node`) that runs a `create_agent` ReAct loop. The agent has two tools:

- `check_product_availability(product_name)` — counts matching products in the database
- `check_product_price(product_name)` — looks up prices for matching products

The query to run is currently hardcoded near the bottom of [main.py](main.py):

```python
query = "what models of RC robot do you have?"
workflow.invoke({"query": query})
```

Each step of the agent's run (including tool calls and tool results) is printed via `agent.stream(...)`.

## Notes

- `content` on Gemini response messages can come back as a list of content blocks (e.g. `{"type": "text", "text": ...}`) rather than a plain string — extract the `text` field(s) rather than printing `content` directly.
- SQL queries against `products` use parameterized `?` placeholders to avoid SQL injection from LLM-generated tool arguments.
