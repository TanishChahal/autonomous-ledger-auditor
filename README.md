# Recon.py: Autonomous Finance Controller

**Recon.py** is a high-throughput, dual-layer reconciliation engine built for the Razorpay AI Buildathon (Track 04: AI Finance Controller). 

It automates the process of reconciling Payment Gateway settlements against Bank statements by combining **deterministic Python logic** with an **Agentic LLM reasoning layer**.

## The Architecture: Why Hybrid?

Processing thousands of transactions through an LLM to check basic arithmetic is expensive, slow, and prone to hallucinations. Audit.py solves this by splitting the workload:

1. **The Deterministic Bouncer (Python + Pydantic)** 
   Instantly parses the ledger, enforces strict data types, and runs exact mathematical comparisons. Perfect matches are immediately saved to the database. (0 API cost, minimal execution time).

2. **The Agentic Detective (OpenAI-Compatible API)**
   When math fails (e.g., missing amounts, messy bank narration strings), the anomalous row is routed to the AI Agent. The Agent is equipped with executable Python tools (`verify_tax_deduction`, `verify_customer_refund`). It calculates the discrepancy, verifies the financial rule, and issues a final, mathematically sound verdict.

3. **The Immutable Ledger (SQLite)**
   Every transaction, whether cleanly matched or AI-resolved, is logged into a structured database to maintain a strict audit trail.

## Quickstart (Local Execution)

This project was built with a zero-bloat backend philosophy. It requires no heavy containers or cloud databases and is optimized to run flawlessly on lightweight hardware.

**Step 1: Setup Environment**
> python3 -m venv venv
> source venv/bin/activate
> pip install pydantic groq

**Step 2: Set API Key**
> export GROQ_API_KEY="your_api_key_here"

**Step 3: Run the Pipeline**
> # Generates a synthetic dataset of 100 transactions
> python3 generate_data.py
>
> # Executes the dual-layer reconciliation pipeline and outputs to SQLite
> python3 main.py

## Tool-Calling Demonstration

When the Agent encounters a discrepancy, it uses executable tools rather than guessing:
* **Input:** Expected `2561.94`, Received `2411.94`. Bank String: `NEFT-RZP-CUST-REFUND`
* **Agent Action:** Triggers `verify_customer_refund` tool.
* **Math Execution:** Calculates delta (150.00) and matches it against standard refund policies.
* **Output:** Saves `AI_RESOLVED` status with specific refund confirmation to the database.

## Tech Stack
* **Language:** Python 3.11
* **Data Validation:** Pydantic
* **AI Provider:** Groq (OpenAI Compatible)
* **Model:** gpt-oss-20b
* **Storage:** SQLite3
