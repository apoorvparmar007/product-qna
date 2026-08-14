"""
Eval harness for the Toy Shop Product QnA chatbot.

Runs golden_eval_set.json against your compiled LangGraph `workflow`,
captures which tools fired and the final answer text, and scores each
case against its expected_tool_calls / answer_must_contain /
answer_must_not_contain criteria.

USAGE
-----
Run from anywhere; it locates the project root (parent of eval/) and
imports `workflow` from main.py there:

    python "run eval.py"

Output: prints a per-case PASS/FAIL/PARTIAL line plus a summary table,
and writes results_<timestamp>.json for diffing against future runs
(this is your regression baseline — commit it or compare manually).

This intentionally does NOT require LangSmith to run. If LangSmith
tracing is wired up, each case's thread_id is printed so you can cross-
reference the trace in the LangSmith UI for deeper debugging.
"""

import json
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

# main.py lives one directory up from eval/, and its DB paths ("database/...")
# are relative to the project root, so make both resolvable.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
import os
os.chdir(PROJECT_ROOT)

from main import workflow

EVAL_SET_PATH = Path(__file__).parent / "golden_eval_set.json"


def load_eval_set():
    with open(EVAL_SET_PATH) as f:
        return json.load(f)["test_cases"]


def build_history_messages(conversation_history):
    """Convert the eval set's plain history format into whatever
    message objects your graph expects. Adjust if you're not using
    LangChain BaseMessage subclasses directly."""
    from langchain_core.messages import HumanMessage, AIMessage

    msgs = []
    for turn in conversation_history:
        if turn["role"] == "user":
            msgs.append(HumanMessage(content=turn["content"]))
        else:
            msgs.append(AIMessage(content=turn["content"]))
    return msgs


def run_case(workflow, case):
    """Runs a single test case through the graph and extracts
    (tool_calls_made, final_answer_text, latency_seconds)."""
    from langchain_core.messages import HumanMessage

    thread_id = f"eval-{case['id']}-{uuid.uuid4().hex[:8]}"
    config = {"configurable": {"thread_id": thread_id}}

    # Prior turns are replayed by seeding the checkpointed history directly,
    # since chat_node only ever sees the latest human turn plus whatever
    # add_messages has accumulated for this thread_id so far.
    history_msgs = build_history_messages(case.get("conversation_history", []))
    if history_msgs:
        workflow.update_state(config, {"chatbot_message": history_msgs})

    input_state = {"chatbot_message": [HumanMessage(content=case["query"])]}

    start = time.time()
    result = workflow.invoke(input_state, config=config)
    latency = time.time() - start

    final_messages = result["chatbot_message"]
    final_answer = final_messages[-1].content if final_messages else ""

    # chat_node runs an inner create_agent() whose tool-calling messages are
    # not part of chatbot_message (only the final text answer is stored
    # there) — main.py's chat_node now surfaces them via state["tool_calls"].
    tool_calls_made = result.get("tool_calls", [])

    return {
        "thread_id": thread_id,
        "final_answer": final_answer,
        "tool_calls_made": tool_calls_made,
        "latency_seconds": round(latency, 2),
    }


def score_case(case, run_result):
    answer = (run_result["final_answer"] or "").lower()
    reasons = []
    passed = True

    for phrase in case.get("answer_must_contain", []):
        if phrase.lower() not in answer:
            passed = False
            reasons.append(f"MISSING expected phrase: '{phrase}'")

    for phrase in case.get("answer_must_not_contain", []):
        if phrase.lower() in answer:
            passed = False
            reasons.append(f"FOUND forbidden phrase: '{phrase}'")

    expected_tools = {t["tool"] for t in case.get("expected_tool_calls", [])}
    actual_tools = {t["tool"] for t in run_result["tool_calls_made"]}
    if expected_tools and expected_tools != actual_tools:
        # Not an auto-fail — flagged as a mismatch for human review,
        # since tool-call *sets* matching isn't always strict pass/fail
        # (e.g. extra exploratory calls may still yield a correct answer).
        reasons.append(
            f"TOOL MISMATCH: expected {sorted(expected_tools)}, got {sorted(actual_tools)}"
        )

    return passed, reasons


def main():
    cases = load_eval_set()
    results = []
    n_pass, n_fail, n_flag = 0, 0, 0

    for case in cases:
        run_result = run_case(workflow, case)
        passed, reasons = score_case(case, run_result)

        status = "PASS" if passed and not reasons else ("FLAG" if passed else "FAIL")
        if status == "PASS":
            n_pass += 1
        elif status == "FLAG":
            n_flag += 1
        else:
            n_fail += 1

        print(f"[{status}] {case['id']} ({case['difficulty']}, {','.join(case['tags'])}) "
              f"— {run_result['latency_seconds']}s")
        print(f"        query: {case['query']}")
        print(f"        answer: {run_result['final_answer']}")
        print(f"        tool_calls: {run_result['tool_calls_made']}")
        if reasons:
            for r in reasons:
                print(f"        {r}")

        results.append({
            "id": case["id"],
            "query": case["query"],
            "status": status,
            "reasons": reasons,
            **run_result,
        })

    print("\n--- SUMMARY ---")
    print(f"PASS: {n_pass}  FLAG: {n_flag}  FAIL: {n_fail}  TOTAL: {len(cases)}")

    out_path = Path(__file__).parent / f"eval_results_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.json"
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Full results written to {out_path.name}")


if __name__ == "__main__":
    main()