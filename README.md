# Autonomous Ledger Auditor: Hybrid Reconciliation Engine

> *Note: The core logic for this microservice was originally engineered during an intensive sprint and has been refactored here as a standalone, production-ready portfolio piece demonstrating FDE integration capabilities.*

The **Autonomous Ledger Auditor** is a high-throughput, dual-layer reconciliation microservice. It automates the process of reconciling messy payment gateway settlements against bank statements by combining deterministic Python validation with an Agentic LLM reasoning layer for anomaly resolution.

## The Architecture: Why Hybrid?

Processing thousands of transactions through an LLM to check basic arithmetic is expensive, slow, and prone to hallucinations. This microservice solves this by splitting the workload:

1. **The Deterministic Bouncer (Python + Pydantic):** Instantly parses the ledger, enforces strict data types, and runs exact mathematical comparisons. Perfect matches are immediately saved to the database. (0 API cost, minimal execution time).
2. **The Agentic Detective (Groq API + Tool Calling):** When math fails (e.g., missing amounts, messy bank narration strings, merged transactions), the anomalous row is routed to the AI Agent. The Agent is equipped with executable Python tools (`verify_tax_deduction`, `verify_customer_refund`). It calculates the discrepancy, verifies the financial rule, and issues a final, mathematically sound verdict.
3. **The Immutable Ledger (SQLite):** Every transaction, whether cleanly matched or AI-resolved, is logged into a structured database to maintain a strict audit trail.

---

## Visual Proof of Execution

### 1. Raw, Unstructured Ledger Input
<img width="1060" height="868" alt="raw_ledger_input" src="https://github.com/user-attachments/assets/103173d0-587a-4f9c-95fd-cd1fb47d86b6" />


### 2. Autonomous Resolution & Audit Output
<img width="1257" height="822" alt="output" src="https://github.com/user-attachments/assets/e2ba8458-96b7-450a-8577-eb0d6d540c64" />

---

## Quickstart (Local Execution)

This project was built with a zero-bloat backend philosophy. It requires no heavy containers or cloud databases and is optimized to run flawlessly on lightweight hardware.

### Step 1: Setup Environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install pydantic groq
```

### Step 2: Set API Key

```bash
export GROQ_API_KEY="your_api_key_here"
```

### Step 3: Run the Pipeline

**Generate a synthetic dataset of 100 transactions:**

```bash
python3 generate_data.py
```

**Execute the dual-layer reconciliation pipeline and output to SQLite:**

```bash
python3 main.py
```

---

## Tool-Calling Demonstration

When the Agent encounters a discrepancy, it uses executable tools rather than guessing:

*   **Input:** Expected `2561.94`, Received `2411.94`. Bank String: `NEFT-RZP-CUST-REFUND`
*   **Agent Action:** Triggers `verify_customer_refund` tool.
*   **Math Execution:** Calculates delta (150.00) and matches it against standard refund policies.
*   **Output:** Saves `AI_RESOLVED` status with specific refund confirmation to the database.

---

## Tech Stack

*   **Language:** Python 3.11
*   **Data Validation:** Pydantic
*   **AI Provider:** Groq (OpenAI Compatible)
*   **Model:** gpt-oss-20b
*   **Storage:** SQLite3
