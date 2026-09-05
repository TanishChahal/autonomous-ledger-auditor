import os
import json
from groq import Groq

# 1. Initialize Groq (it automatically picks up the GROQ_API_KEY from your terminal)
client = Groq()
# Using Llama 3.3 70B because it is blazing fast and excellent at tool calling
MODEL = "openai/gpt-oss-20b"

# ==========================================
# TOOL DEFINITIONS (The Agent's "Hands")
# ==========================================

def verify_tax_deduction(expected_amount: float, actual_amount: float) -> str:
    """Tool for the AI to calculate if the discrepancy is exactly a 2% Tax Deduction (TDS)."""
    expected_tax = round(expected_amount * 0.02, 2)
    difference = round(expected_amount - actual_amount, 2)
    
    if difference == expected_tax:
        return json.dumps({"status": "CONFIRMED", "reason": f"Exact 2% TDS match (₹{difference})"})
    return json.dumps({"status": "FAILED", "reason": f"Difference ₹{difference} does not match 2% tax (₹{expected_tax})"})

def verify_customer_refund(expected_amount: float, actual_amount: float) -> str:
    """Tool for the AI to calculate if the discrepancy is a standard ₹150 flat refund deduction."""
    difference = round(expected_amount - actual_amount, 2)
    if difference == 150.00:
        return json.dumps({"status": "CONFIRMED", "reason": "Standard ₹150 refund deducted."})
    return json.dumps({"status": "FAILED", "reason": f"Difference ₹{difference} is not ₹150."})

# 1.1 Map the tool names to the actual Python functions
available_tools = {
    "verify_tax_deduction": verify_tax_deduction,
    "verify_customer_refund": verify_customer_refund,
}

# 1.2 Define the tool schemas so the AI knows how to use them
tools_schema = [
    {
        "type": "function",
        "function": {
            "name": "verify_tax_deduction",
            "description": "Calculate if a missing amount perfectly matches a 2% TDS tax.",
            "parameters": {
                "type": "object",
                "properties": {
                    "expected_amount": {"type": "number", "description": "The expected original amount"},
                    "actual_amount": {"type": "number", "description": "The actual amount received in bank"}
                },
                "required": ["expected_amount", "actual_amount"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "verify_customer_refund",
            "description": "Check if a missing amount matches the standard 150 INR customer refund deduction.",
            "parameters": {
                "type": "object",
                "properties": {
                    "expected_amount": {"type": "number", "description": "The expected original amount"},
                    "actual_amount": {"type": "number", "description": "The actual amount received in bank"}
                },
                "required": ["expected_amount", "actual_amount"]
            }
        }
    }
]

# ==========================================
# THE AGENT LOOP (The AI Brain)
# ==========================================

def analyze_exception(transaction_data: dict):
    print(f"\n---  Agent Investigating: {transaction_data['transaction_id']} ---")
    
    messages = [
        {"role": "system", "content": "You are a senior finance reconciliation AI. Use the provided tools to calculate if a missing payment amount is due to standard taxes or refunds based on the bank narration and amounts."},
        {"role": "user", "content": f"Investigate this mismatch: {json.dumps(transaction_data)}"}
    ]

    # Step A: The AI decides what to do
    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        tools=tools_schema,
        tool_choice="auto",
    )
    
    response_message = response.choices[0].message
    messages.append(response_message)

    # Step B: Did the AI decide to use a tool?
    if response_message.tool_calls:
        for tool_call in response_message.tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)
            
            print(f" Agent triggered tool: `{function_name}` with args: {function_args}")
            
            # Execute the python tool
            tool_func = available_tools[function_name]
            tool_result = tool_func(**function_args)
            
            # Feed the tool's result back to the AI
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "name": function_name,
                "content": tool_result,
            })
            
        # Step C: The AI generates the final verdict using the tool's math
        final_response = client.chat.completions.create(
            model=MODEL,
            messages=messages
        )
        return final_response.choices[0].message.content
    else:
        # The AI figured it out without tools 
        return response_message.content

# ==========================================
# TEST IT OUT
# ==========================================
if __name__ == "__main__":
    # Let's manually feed it the exception you got in your terminal earlier
    test_record = {
        "transaction_id": "txn_1ec34a35",
        "date": "2026-08-10",
        "expected_rzp_amount": 2561.94,
        "actual_bank_amount": 2411.94,
        "bank_narration": "NEFT-RZP-CUST-REFUND-DED-TXN_1EC34A35"
    }
    
    analyze_exception(test_record)