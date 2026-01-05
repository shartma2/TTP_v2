from datetime import datetime
import os
import json
import logging

LOGS_DIR = "/app/backend/logs"

logger = logging.getLogger(__name__)

def log(response, module, model, temperature, base_url, api_key, messages):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
    try:
        resp_dict = response.model_dump()
    except Exception as e_json:
        logger.warning("Failed to serialize response with model_dump(): %s", e_json)
        try:
            resp_dict = response.__dict__
        except Exception as e_dict:
            logger.warning("Failed to serialize response using __dict__: %s. Falling back to string representation.", e_dict)
            resp_dict = {"raw": str(response)}

    log_entry = {
        "timestamp": ts,
        "request": {
            "model": model,
            "temperature": temperature,
            "base_url": base_url,
            "api_key_present": bool(api_key),
        },
        "messages": messages,
        "response": resp_dict,
    }

    # Ensure container logs directory exists and write JSON log
    os.makedirs(LOGS_DIR, exist_ok=True)
    log_filename = f"{module}_{ts}.json"
    log_path = os.path.join(LOGS_DIR, log_filename)
    with open(log_path, "w", encoding="utf-8") as f:
        json.dump(log_entry, f, ensure_ascii=False, indent=2)
