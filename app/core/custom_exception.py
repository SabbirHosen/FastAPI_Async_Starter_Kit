class CustomException(Exception):
    def __init__(self, name: str, detail: str, error_code: int = 400):
        self.name = name
        self.detail = detail
        self.error_code = error_code
        super().__init__(self._generate_message())

    def _generate_message(self) -> str:
        return f"{self.name} (Error Code: {self.error_code}): {self.detail}"

    def __str__(self):
        return self._generate_message()

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "detail": self.detail,
            "error_code": self.error_code
        }
