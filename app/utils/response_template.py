from fastapi import HTTPException
from typing import Any, Dict
from fastapi.responses import JSONResponse

def success_response(data: Any, message: str = "Success") -> Dict[str, Any]:
    return {
        "status": "Successfully",
        "message": message,
        "data": data
    }

def fail_response(message: str = "Fail", data: Any = None) -> Dict[str, Any]:
    return {
        "status": "Fail",
        "message": message,
        "data": data
    }

def bad_request_response(detail: str = "Bad request") -> None:
    raise HTTPException(status_code=400, detail=detail)


def success(message: str, data: any):
    content = {
        "message": message,
        "data": data,
        "result": 1
    }
    return JSONResponse(
        status_code=200,
        content=content
    )


def failure(message: str, data: None):
    content = {
        "message": message,
        "data": data,
        "result": -1
    }
    return JSONResponse(
        status_code=400,
        content=content
    )

def custom_response(status_code: int, result: int, message: str, data: Any = None):
    content = {
        "message": message,
        "data": data,
        "result": result
    }
    return JSONResponse(
        status_code=status_code,
        content=content
    )
