from fastapi import HTTPException

class APIRequestException(HTTPException):
    def __init__(self, detail: str, status_code: int = 500):
        super().__init__(status_code=status_code, detail=detail)

class InvalidDateFormatException(HTTPException):
    def __init__(self, detail: str = "Dates must be in 'YYYY-MM-DDTHH:MM' format"):
        super().__init__(status_code=400, detail=detail)

class DateRangeException(HTTPException):
    def __init__(self, detail: str = "from_date must be earlier than or equal to to_date"):
        super().__init__(status_code=400, detail=detail)

class InvalidResponseException(HTTPException):
    def __init__(self, detail: str):
        super().__init__(status_code=500, detail=detail)