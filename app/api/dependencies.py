from fastapi import Header, Depends
from typing import Tuple

async def get_auth_headers(
    x_token: str = Header(...), x_refresh_token: str = Header(...)
) -> Tuple[str, str]:
    return x_token, x_refresh_token