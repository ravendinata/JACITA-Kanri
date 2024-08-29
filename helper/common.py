import uuid

def generate_txn_id(category: str):
    return f"{category}-{str(uuid.uuid4())[:16].upper()}"