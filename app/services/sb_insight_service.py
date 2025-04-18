import json
from typing import Dict, List, Optional

from app.services.sb_api_service import APISentimentAggregationService
from app.services.sov_api_service import APISovService
from app.core.exceptions import APIRequestException

class SentimentBreakdownInsightService:
    def __init__(self, x_token: str, x_refresh_token: str):
        self.api_service = APISentimentAggregationService(x_token, x_refresh_token)

    async def generate_insight(
        self,
        topic_ids: List[str],
        from_date1: str,
        to_date1: str,
        from_date2: str,
        to_date2: str,
    ) -> Optional[str]:
        try:
            sentiment_data: dict = self.api_service.get_sentiment_breakdown_competitor(topic_ids, from_date1, to_date1, from_date2, to_date2)
            prompt = self.build_sentiment_breakdown_prompt(sentiment_data)

            response = self.api_service.openai_client.chat.completions.create(
                model="meta-llama/llama-4-scout:free",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1500,
                temperature=0.7,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"[LỖI] Không thể tạo insight: {str(e)}"

    def build_sentiment_breakdown_prompt( self, sentiment_data: dict
    ) -> str:
        from_date1 = sentiment_data["data_preiod_1"]["from_date"]
        to_date1 = sentiment_data["data_preiod_1"]["to_date"]
        from_date2 = sentiment_data["data_preiod_2"]["from_date"]
        to_date2 = sentiment_data["data_preiod_2"]["to_date"]

        return f"""
    Dữ liệu phân tích cảm xúc (Sentiment Breakdown) của các thương hiệu theo hai giai đoạn:

    ### Giai đoạn 1 ({from_date1} - {to_date1})
    {json.dumps(sentiment_data["data_preiod_1"]["data"], ensure_ascii=False, indent=2)}

    ### Giai đoạn 2 ({from_date2} - {to_date2})
    {json.dumps(sentiment_data["data_preiod_2"]["data"], ensure_ascii=False, indent=2)}

    ### Yêu cầu
    Bạn là một chuyên gia phân tích dữ liệu. Hãy viết **báo cáo insight cảm xúc** bằng tiếng Việt, ngắn gọn, dễ hiểu, chuyên nghiệp. Nội dung cần có:

    1. **Tổng quan cảm xúc**: Nhận định tổng quan về cảm xúc tích cực, tiêu cực, trung lập của các thương hiệu giữa hai giai đoạn.
    2. **So sánh chi tiết từng thương hiệu**: Đánh giá thay đổi cảm xúc theo từng thương hiệu giữa 2 giai đoạn.
    3. **Xu hướng và nhận định**: Rút ra xu hướng cảm xúc (tăng/giảm tích cực, tiêu cực), lý do có thể (nếu có).
    4. **Khuyến nghị hành động**: Đề xuất hành động truyền thông phù hợp cho từng thương hiệu dựa trên diễn biến cảm xúc.

    Chỉ tập trung vào insight từ số liệu cảm xúc, tránh lặp lại dữ liệu gốc hoặc nêu lại quá chi tiết.
    """
