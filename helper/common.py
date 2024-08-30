import uuid

def generate_txn_id(category: str):
    return f"{category}-{str(uuid.uuid4())[:16].upper()}"

def convert_seconds_to_human_readable(seconds: int):
    months = seconds // 2592000
    days = seconds // 86400 % 30
    hours = seconds // 3600 % 24
    minutes = seconds // 60 % 60

    formatted_time = ""

    if months > 0:
        formatted_time += f"{months}mo "

    if days > 0:
        formatted_time += f"{days}d "
    
    if hours > 0:
        formatted_time += f"{hours}h "

    if minutes > 0:
        formatted_time += f"{minutes}min "

    return formatted_time.strip()