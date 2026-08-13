# Product QnA

A LangGraph agent that answers questions about toy shop inventory — product availability and pricing — by querying a local SQLite database. Built with LangChain's `create_agent` and a local Ollama model (`qwen3:8b`), with a Streamlit chat interface and persistent conversation history via `SqliteSaver`.

## Requirements

- Python 3.10+ (LangChain's `create_agent` requires it)
- [Ollama](https://ollama.com) running locally with the `qwen3:8b` model pulled (`ollama pull qwen3:8b`)
- A `database/toyshop.db` SQLite file with a `products` table (`id`, `name`, `category`, `brand`, `age_group`, `price`, `stock_qty`, `delivery_days`)
- Python packages: `langchain`, `langchain-ollama`, `langgraph`, `langgraph-checkpoint-sqlite`, `streamlit`, `python-dotenv`

## Setup

```bash
python3 -m venv .product
source .product/bin/activate
pip install langchain langchain-ollama langgraph langgraph-checkpoint-sqlite streamlit python-dotenv
```

## Usage

### Chat UI

```bash
streamlit run frontend.py
```

This launches a Streamlit chat interface backed by the LangGraph workflow in [main.py](main.py). Each conversation is tracked by a `thread_id`; past threads are listed in the sidebar (persisted in `database/checkpoint.db`), and "New Chat" starts a fresh thread.

The agent has two tools (defined in [tools.py](tools.py)):

- `check_product_availability(product_name)` — counts matching products in the database
- `check_product_price(product_name)` — looks up prices for matching products

### Database utilities

- `python3 add_records.py [N]` — inserts `N` randomly generated toy product records into `products` (defaults to 10).
- `python3 view_db.py [N]` — prints a formatted table of up to `N` rows from `products`, plus the total record count (defaults to 20).

## Notes

- SQL queries against `products` use parameterized `?` placeholders to avoid SQL injection from LLM-generated tool arguments.
- Conversation state and checkpoints are stored in `database/checkpoint.db` via LangGraph's `SqliteSaver`, separate from the product data in `database/toyshop.db`.
