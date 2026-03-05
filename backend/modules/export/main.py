from typing import Any
import base64

def run(payload: dict[str, Any]) -> dict[str, Any]:
    content = b"hello export"

    result = {
        "fileName": "test.txt",
        "contentType": "text/plain; charset=utf-8",
        "sizeBytes": len(content),
        "dataBase64": base64.b64encode(content).decode("utf-8"),
    }

    return {"response": result}