from requests import HTTPError, Response


class SwishError(HTTPError):
    errors = None
    raw_errors = None
    trace_id = None

    def __init__(self, errors: object, *, response: Response | None = None):
        self.raw_errors = errors
        error_items = errors if isinstance(errors, list) else [errors]
        self.trace_id = next((e.get("traceId") for e in error_items if isinstance(e, dict) and e.get("traceId")), None)
        self.errors = {
            str(e.get("errorCode", e.get("code", "error"))): str(e.get("errorMessage", e.get("message", str(e))))
            for e in error_items
            if isinstance(e, dict) and e
        }
        if not self.errors:
            message = f"HTTP {response.status_code}" if response is not None and not errors else str(errors)
            self.errors = {"error": message}
        super().__init__(", ".join([f"{k}: {v}" for k, v in self.errors.items()]), response=response)
