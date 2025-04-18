import json
from fastapi import APIRouter, Depends, Request
from cachetools import TTLCache
from app.models.request_models import InsightRequest
from app.models.response_models import SOVInsightResponse
from app.services.sov_insight_service import SovInsightService
from app.api.dependencies import get_auth_headers
from app.utils import response_template

router = APIRouter(prefix="/sov", tags=["SOV Insights"])

# Khởi tạo cache với TTL 1800 giây và tối đa 1000 item
cache = TTLCache(maxsize=1000, ttl=1800)

@router.post("/generate_insight")
async def generate_sov_insight(
    request: InsightRequest,
    http_request: Request,
    auth_headers: tuple = Depends(get_auth_headers),
):
    # Tạo cache key từ path và body
    body_bytes = await http_request.body()
    body_json = json.loads(body_bytes)
    cache_key = json.dumps({
        "path": str(http_request.url.path),
        "body": body_json
    }, sort_keys=True)

    # Trả kết quả từ cache nếu có
    if cache_key in cache:
        return response_template.success_response(data=cache[cache_key])

    # Nếu chưa có cache, gọi service
    x_token, x_refresh_token = auth_headers
    insight_service = SovInsightService(x_token, x_refresh_token)
    report, data_period1, data_period2 = await insight_service.generate_insight(
        topic_ids=request.topic_ids,
        from_date1=request.from_date1,
        to_date1=request.to_date1,
        from_date2=request.from_date2,
        to_date2=request.to_date2,
    )

    if report is None:
        return response_template.fail_response("Failed to generate SOV report")

    result = {
        "report": report,
        "data_period_1": data_period1,
        "data_period_2": data_period2,
    }

    # Lưu vào cache
    cache[cache_key] = result

    return response_template.success_response(data=result)