class SwishError(Exception):
    errors = None
    raw_errors = None
    trace_id = None

    def __init__(self, errors: list[dict] | dict | str):
        self.raw_errors = errors
        error_items = errors if isinstance(errors, list) else [errors]
        self.trace_id = next((e.get("traceId") for e in error_items if isinstance(e, dict) and e.get("traceId")), None)
        self.errors = {
            e.get("errorCode", e.get("code", "error")): e.get("errorMessage", e.get("message", str(e)))
            for e in error_items
            if isinstance(e, dict)
        }
        if not self.errors:
            self.errors = {"error": str(errors)}
        super().__init__(", ".join([f"{k}: {v}" for k, v in self.errors.items()]))
