import csv
from pydantic import BaseModel, ValidationError
from typing import List
from pathlib import Path

# Always resolve paths relative to engine.py's location
BASE_DIR = Path(__file__).resolve().parent
CSV_PATH = BASE_DIR / "settlements.csv"

# 1. Define the strict schema for our incoming data
class Transaction(BaseModel):
    transaction_id: str
    date: str
    expected_rzp_amount: float
    actual_bank_amount: float
    bank_narration: str
    
    # 2. Pure Python logic to check for a perfect financial match
    @property
    def is_match(self) -> bool:
        # Using a strict equality check. In real world, we might add a small tolerance.
        return self.expected_rzp_amount == self.actual_bank_amount

def run_reconciliation(file_path: str):
    matched_records = []
    exception_records = []
    
    with open(file_path, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            try:
                # 3. Pydantic instantly validates the raw text into Python objects
                txn = Transaction(**row)
                
                # 4. The Routing Logic
                if txn.is_match:
                    matched_records.append(txn)
                else:
                    exception_records.append(txn)
            except ValidationError as e:
                print(f"Format error in row {row.get('transaction_id')}: {e}")
                
    # 5. The Audit Output
    print(f"Total Processed: {len(matched_records) + len(exception_records)}")
    print(f" Auto-Reconciled (Math verified): {len(matched_records)}")
    print(f" Exceptions Flagged for AI: {len(exception_records)}")
    
    return matched_records, exception_records

if __name__ == "__main__":
    print("Initializing Deterministic Engine...\n")
    matched, exceptions = run_reconciliation("settlements.csv")
    
    if exceptions:
        print("\n--- Sample Exception Data (Next stop: LLM API) ---")
        # Dump the first exception to JSON so we can easily feed it to the AI prompt later
        print(exceptions[0].model_dump_json(indent=2))