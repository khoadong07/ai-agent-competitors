import json
from fastapi import APIRouter, Depends, Request
from app.models.request_models import InsightRequest
from app.services.sov_insight_service import SovInsightService
from app.api.dependencies import get_auth_headers
from app.utils import response_template
from cachetools import TTLCache

router = APIRouter(prefix="/band-attribute", tags=["Brand Attribute by Sentiment Insights"])

cache = TTLCache(maxsize=1000, ttl=1800)

@router.post("/generate_insight")
async def generate_brand_attribute_by_sentiment_insight(
        request_data: InsightRequest,
        request: Request,
        auth_headers: tuple = Depends(get_auth_headers),
):
    # Tạo cache key từ path và body
    body_bytes = await request.body()
    body_json = json.loads(body_bytes)
    cache_key = json.dumps({
        "path": str(request.url.path),
        "body": body_json
    }, sort_keys=True)

    # Kiểm tra cache
    if cache_key in cache:
        return response_template.success_response(data=cache[cache_key])

    # Gọi service nếu chưa có trong cache
    x_token, x_refresh_token = auth_headers
    insight_service = SovInsightService(x_token, x_refresh_token)
    report, data_period1, data_period2 = await insight_service.generate_insight(
        topic_ids=request_data.topic_ids,
        from_date1=request_data.from_date1,
        to_date1=request_data.to_date1,
        from_date2=request_data.from_date2,
        to_date2=request_data.to_date2,
    )

    if report is None:
        return response_template.fail_response("Failed to generate Brand Attribute report")

    result = {"report": report, "data_period_1": data_period1, "data_period_2": data_period2}

    # Lưu kết quả vào cache
    cache[cache_key] = result

    return response_template.success_response(data=result)