import json
from fastapi import APIRouter, Depends
from app.models.request_models import InsightRequest
from app.models.response_models import SOVInsightResponse
from app.services.sov_insight_service import SovInsightService
from app.api.dependencies import get_auth_headers
from app.utils import response_template

router = APIRouter(prefix="/channel-breakdown", tags=["Channel Breakdown Insights"])

@router.post("/generate_insight")
async def generate_brand_attribute_by_sentiment_insight(
    request: InsightRequest,
    auth_headers: tuple = Depends(get_auth_headers),
):
    x_token, x_refresh_token = auth_headers
    insight_service = SovInsightService(x_token, x_refresh_token)
    report, data_period1, data_period2 = await insight_service.generate_insight(
        topic_ids=request.topic_ids,
        from_date1=request.from_date1,
        to_date1=request.to_date1,
        from_date2=request.from_date2,
        to_date2=request.to_date2,
    )
    print(type(data_period1))
    print(type(data_period2))
    if report is None:
        return response_template.fail_response("Failed to generate Channel Breakdown report")
    return response_template.success_response(data={"report": report, "data_period_1": data_period1, "data_period_2": data_period2})