from typing import Any


class CustomException(Exception):
    def __init__(self, message: str, extra_info: Any) -> None:
        super().__init__(message)
        self.extra_info = extra_info
