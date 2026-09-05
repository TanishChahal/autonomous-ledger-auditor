import csv
import random
import uuid
from datetime import datetime, timedelta

def generate_ledger(filename="settlements.csv", num_records=100):
    headers = [
        "transaction_id", "date", "expected_rzp_amount", 
        "actual_bank_amount", "bank_narration", "true_anomaly_type"
    ]
    
    records = []
    base_date = datetime.now()

    for i in range(num_records):
        tx_id = f"txn_{uuid.uuid4().hex[:8]}"
        date = (base_date - timedelta(days=random.randint(0, 30))).strftime("%Y-%m-%d")
        
        # Base amount between ₹500 and ₹5000
        base_amount = round(random.uniform(500.0, 5000.0), 2)
        
        # Determine if this record will be a clean match or an error (80% clean, 20% errors)
        scenario = random.choices(
            ["CLEAN", "TAX_DEDUCTION", "PARTIAL_REFUND", "GARBLED_DESC"], 
            weights=[80, 5, 10, 5]
        )[0]

        if scenario == "CLEAN":
            expected = base_amount
            actual = base_amount
            narration = f"NEFT-RZP-SETTLEMENT-{tx_id.upper()}"
            
        elif scenario == "TAX_DEDUCTION":
            expected = base_amount
            actual = round(base_amount * 0.98, 2) # 2% TDS deducted
            narration = f"RTGS-RZP-TDS-ADJ-{tx_id.upper()[:4]}"
            
        elif scenario == "PARTIAL_REFUND":
            expected = base_amount
            actual = round(base_amount - 150.0, 2) # Flat 150 deduction
            narration = f"NEFT-RZP-CUST-REFUND-DED-{tx_id.upper()}"
            
        elif scenario == "GARBLED_DESC":
            expected = base_amount
            actual = base_amount # Amount is right, but text is a mess
            narration = f"SYSTEM_ERR_RETRY_{random.randint(1000,9999)}_RZP"

        records.append([tx_id, date, expected, actual, narration, scenario])

    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(headers)
        writer.writerows(records)
    
    print(f"Generated {num_records} records in {filename}")

if __name__ == "__main__":
    generate_ledger(num_records=100)