import json
from typing import Dict, List, Optional
from app.services.sov_api_service import APISovService
from app.core.exceptions import APIRequestException

class SovInsightService:
    def __init__(self, x_token: str, x_refresh_token: str):
        self.api_service = APISovService(x_token, x_refresh_token)

    async def generate_insight(
        self,
        topic_ids: List[str],
        from_date1: str,
        to_date1: str,
        from_date2: str,
        to_date2: str,
    ) -> Optional[str]:
        try:
            data_period_1 = self.api_service.get_sov_data(topic_ids, from_date1, to_date1)
            data_period_2 = self.api_service.get_sov_data(topic_ids, from_date2, to_date2)
            topic_data = [
                self.api_service.get_topic_by_topic_id(topic_id) for topic_id in topic_ids
            ]
            topic_data = [topic for topic in topic_data if topic]  # Filter out None values

            prompt, buzz_data_1, buzz_data_2 = self._build_prompt(
                data_period_1,
                data_period_2,
                topic_data,
                from_date1,
                to_date1,
                from_date2,
                to_date2,
            )

            response = self.api_service.openai_client.chat.completions.create(
                model="meta-llama/llama-4-scout:free",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1500,
                temperature=0.7,
            )
            return response.choices[0].message.content.strip(), buzz_data_1, buzz_data_2
        except Exception as e:
            return f"[LỖI] Không thể tạo insight: {str(e)}"

    def _build_prompt(
        self,
        data_period_1: Dict,
        data_period_2: Dict,
        topic_map: List[Dict],
        from_date1: str,
        to_date1: str,
        from_date2: str,
        to_date2: str,
    ) -> str:
        buzz_data_1 = [
            self.api_service.get_buzz_data(topic["_id"], from_date1, to_date1)
            for topic in topic_map
        ]
        buzz_data_2 = [
            self.api_service.get_buzz_data(topic["_id"], from_date2, to_date2)
            for topic in topic_map
        ]

        return f"""
        Dữ liệu Share of Voice (SOV) cho hai giai đoạn:

        ### Giai đoạn 1 ({from_date1} - {to_date1})
        **SOV**: 
        {json.dumps(data_period_1, ensure_ascii=False, indent=2)}
        **Buzz có tương tác cao**:
        {json.dumps(buzz_data_1, ensure_ascii=False, indent=2)}

        ### Giai đoạn 2 ({from_date2} - {to_date2})
        **SOV**:
        {json.dumps(data_period_2, ensure_ascii=False, indent=2)}
        **Buzz có tương tác cao**:
        {json.dumps(buzz_data_2, ensure_ascii=False, indent=2)}

        ### Ánh xạ topic
        {json.dumps([{"_id": topic["_id"], "name": topic["name"]} for topic in topic_map], ensure_ascii=False, indent=2)}

        ### Yêu cầu
        Bạn là AI phân tích dữ liệu chuyên nghiệp. Tạo báo cáo insight bằng tiếng Việt, văn phong rõ ràng, chuyên nghiệp, gồm:
        1. **Tổng quan**: Tóm tắt ngắn gọn về SOV của hai giai đoạn.
        2. **Phân tích chi tiết**: So sánh SOV của từng topic (dùng tên topic) giữa hai giai đoạn.
        3. **Xu hướng và khuyến nghị**: Nhận định thay đổi SOV và đề xuất 1-2 hành động cụ thể.
        4. **Buzz nổi bật**: Tóm tắt mỗi buzz có tương tác cao (dưới 50 từ) và trích dẫn URL làm dẫn chứng.

        Đảm bảo báo cáo ngắn gọn, súc tích, tập trung vào insight hữu ích.
        """, buzz_data_1, buzz_data_2