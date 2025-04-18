from fastapi import APIRouter, Depends
from app.models.request_models import InsightRequest
from app.services.sb_insight_service import SentimentBreakdownInsightService
from app.api.dependencies import get_auth_headers
from app.utils import response_template

router = APIRouter(prefix="/sentiment_breakdown", tags=["SB Insights"])

@router.post("/generate_insight")
async def generate_sov_insight(
    request: InsightRequest,
    auth_headers: tuple = Depends(get_auth_headers),
):
    x_token, x_refresh_token = auth_headers
    insight_service = SentimentBreakdownInsightService(x_token, x_refresh_token)
    report = await insight_service.generate_insight(
        topic_ids=request.topic_ids,
        from_date1=request.from_date1,
        to_date1=request.to_date1,
        from_date2=request.from_date2,
        to_date2=request.to_date2,
    )
    if report is None:
        return response_template.fail_response("Failed to generate Sentiment Breakdown report")
    return response_template.success_response(data={"report": report})