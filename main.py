import sqlite3
import json
from engine import run_reconciliation
from agent import analyze_exception

# 1. Setup SQLite Database
def setup_db():
    conn = sqlite3.connect("ledger.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS audit_log (
            transaction_id TEXT PRIMARY KEY,
            date TEXT,
            expected_amount REAL,
            actual_amount REAL,
            status TEXT,
            ai_verdict TEXT
        )
    ''')
    conn.commit()
    return conn

def main():
    print("Starting AI Finance Controller Pipeline...\n")
    
    # 2. Initialize DB
    conn = setup_db()
    cursor = conn.cursor()
    
    # 3. Run the Deterministic Engine
    matched, exceptions = run_reconciliation("settlements.csv")
    
    # 4. Fast-path: Log clean matches instantly
    for txn in matched:
        cursor.execute('''
            INSERT OR IGNORE INTO audit_log 
            (transaction_id, date, expected_amount, actual_amount, status, ai_verdict)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (txn.transaction_id, txn.date, txn.expected_rzp_amount, txn.actual_bank_amount, "CLEAN_MATCH", "N/A - Math Verified"))
    conn.commit()
    print(f" Saved {len(matched)} clean records to SQLite.")

    # 5. Slow-path: Route exceptions to AI Agent
    print(f"\nProcessing {len(exceptions)} exceptions through AI Agent...")
    for txn in exceptions:
        # Convert Pydantic object to dict for the agent
        txn_dict = txn.model_dump()
        
        # Get AI reasoning
        verdict = analyze_exception(txn_dict)
        
        # Save to DB
        cursor.execute('''
            INSERT OR IGNORE INTO audit_log 
            (transaction_id, date, expected_amount, actual_amount, status, ai_verdict)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (txn.transaction_id, txn.date, txn.expected_rzp_amount, txn.actual_bank_amount, "AI_RESOLVED", verdict))
    
    conn.commit()
    conn.close()
    print("\n Pipeline Complete. All records saved to ledger.db")

if __name__ == "__main__":
    main()