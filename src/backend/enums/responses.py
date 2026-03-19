from enum import Enum

class ResponseSignal(Enum):
   
     # ── 1xxx Infrastructure ─────────────────────────────
    HTTP_500_INTERNAL_SERVER_ERROR = "ERR-1000 | Internal server error"
    HTTP_502_BAD_GATEWAY           = "ERR-1001 | Bad gateway"
    SERVICE_UNAVAILABLE            = "ERR-1002 | Service unavailable"

    # ── 2xxx Session ────────────────────────────────────
    SESSION_CREATED                = "OK-2000  | Session created"
    SESSION_CLEARED                = "OK-2001  | Session cleared"
    SESSION_NOT_FOUND              = "ERR-2002 | Session not found"

    # ── 3xxx LLM ────────────────────────────────────────
    LLM_RESPONSE_SUCCESS           = "OK-3000  | LLM response success"
    LLM_RESPONSE_ERROR             = "ERR-3001 | LLM call failed"
    LLM_RATE_LIMIT                 = "ERR-3002 | LLM rate limit exceeded"
    LLM_CONNECTION_ERROR           = "ERR-3003 | LLM connection error"

    # ── 5xxx Validation ──────────────────────────────────
    INVALID_INPUT                  = "ERR-5000 | Invalid input"
    MESSAGE_TOO_LONG               = "ERR-5001 | Message too long"

    # ── 4xxx Ingestion ───────────────────────────────────
    FILE_TYPE_NOT_SUPPORTED = "ERR-4000 | File type not supported"
    FILE_UPLOAD_FAILED      = "ERR-4001 | File upload failed"
    FILE_EMPTY              = "ERR-4002 | Document has no readable text"