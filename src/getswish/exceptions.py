class SwishError(Exception):
    errors = None

    def __init__(self, errors: list[dict]):
        self.errors = {e["errorCode"]: e["errorMessage"] for e in errors}
        super().__init__(", ".join([f"{k}: {v}" for k, v in self.errors.items()]))
