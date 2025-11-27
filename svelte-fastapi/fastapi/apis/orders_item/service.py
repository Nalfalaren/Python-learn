import base64
import json

def encode_cursor(last_item):
    obj = {
        "date": last_item.created_at.isoformat() if last_item.created_at else None,
        "id": last_item.id,
    }
    return base64.b64encode(json.dumps(obj).encode("utf-8")).decode("utf-8")

def decode_cursor(next_cursor: str):
    try:
        decoded_json = base64.b64decode(next_cursor).decode("utf-8")
        return json.loads(decoded_json)
    except Exception:
        return None
