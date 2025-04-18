import requests
from datetime import datetime
from typing import List, Optional, Dict
from app.core.config import settings
from app.core.exceptions import APIRequestException, InvalidDateFormatException, DateRangeException, InvalidResponseException
from openai import OpenAI


class APISentimentAggregationService:
    def __init__(self, x_token: str, x_refresh_token: str):
        self.x_token = x_token
        self.x_refresh_token = x_refresh_token
        self.openai_client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=settings.OPENROUTER_API_KEY,
        )

    def _get_headers(self) -> Dict[str, str]:
        return {
            'accept': 'application/graphql-response+json, application/json',
            'content-type': 'application/json',
            'user-agent': (
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36'
            ),
            'x-refresh-token': self.x_refresh_token,
            'x-token': self.x_token,
        }

    import json
    from typing import List, Dict

    def refactor_result(self, results: Dict, topics: List[Dict], from_date: str, to_date: str) -> Dict:
        # Tạo dict để tra nhanh tên theo topic_id
        topic_map = {f"topic{t['_id']}": t['name'] for t in topics}

        # Kết quả trả về
        mapped_result = {
            "from_date": from_date,
            "to_date": to_date,
            "data": []
        }

        for bucket in results.get("_index_terms", {}).get("buckets", []):
            topic_id = bucket["key"]
            topic_name = topic_map.get(topic_id, topic_id)

            # Khởi tạo giá trị sentiment
            sentiment_counts = {"positive": 0, "neutral": 0, "negative": 0}
            for sentiment in bucket.get("sentiment.value_terms", {}).get("buckets", []):
                key = sentiment["key"]
                count = sentiment["doc_count"]
                if key == 1:
                    sentiment_counts["negative"] = count
                elif key == 2:
                    sentiment_counts["neutral"] = count
                elif key == 3:
                    sentiment_counts["positive"] = count

            # Thêm vào danh sách kết quả
            mapped_result["data"].append({
                "topic_name": topic_name,
                "total": bucket.get("doc_count", 0),
                "sentiment": sentiment_counts
            })

        return mapped_result

    def validate_date_format(self, date_str: str) -> bool:
        try:
            datetime.strptime(date_str, "%Y-%m-%dT%H:%M")
            return True
        except ValueError:
            return False

    def get_sentiment_aggregation(
        self,
        topic_ids: List[str],
        from_date: str,
        to_date: str
    ) -> Optional[Dict]:
        if not (self.validate_date_format(from_date) and self.validate_date_format(to_date)):
            raise InvalidDateFormatException()

        from_dt = datetime.strptime(from_date, "%Y-%m-%dT%H:%M")
        to_dt = datetime.strptime(to_date, "%Y-%m-%dT%H:%M")
        if from_dt > to_dt:
            raise DateRangeException()

        payload = {
            "query": """
                query Aggregations($input: IndexesInput!, $filter: FilterBuzzInput, $aggs: [AggregationTypeInput]!) {
                    aggregations(input: $input, filter: $filter, aggs: $aggs) {
                        status
                        message
                        data
                    }
                }
            """,
            "variables": {
                "input": {"indexes": topic_ids},
                "aggs": [
                    {
                        "type": "TERMS",
                        "field": "INDEX",
                        "option": {"terms": {"size": 100}},
                        "nest": [
                            {
                                "type": "TERMS",
                                "field": "SENTIMENT",
                                "option": {"terms": {"size": 100}},
                            }
                        ],
                    }
                ],
                "filter": {
                    "publishedFromDate": from_date,
                    "publishedToDate": to_date,
                    "types": [
                        "FBPAGE_TOPIC", "FBPAGE_COMMENT", "FBGROUP_TOPIC", "FBGROUP_COMMENT",
                        "FBUSER_TOPIC", "FBUSER_COMMENT", "FORUM_TOPIC", "FORUM_COMMENT",
                        "NEWS_TOPIC", "NEWS_COMMENT", "YOUTUBE_TOPIC", "YOUTUBE_COMMENT",
                        "BLOG_TOPIC", "BLOG_COMMENT", "QA_TOPIC", "QA_COMMENT",
                        "SNS_TOPIC", "SNS_COMMENT", "TIKTOK_TOPIC", "TIKTOK_COMMENT",
                        "LINKEDIN_TOPIC", "LINKEDIN_COMMENT", "ECOMMERCE_TOPIC", "ECOMMERCE_COMMENT",
                        "THREADS_TOPIC", "THREADS_COMMENT",
                    ],
                    "isDeleted": False,
                    "sentiments": ["POSITIVE", "NEGATIVE", "NEUTRAL"],
                    "labels": self.get_label_ids_by_topic_id(topic_ids[0]),
                    "levels": ["NONE", "LEVEL_1", "LEVEL_2", "LEVEL_3"]
                }
            }
        }

        try:
            response = requests.post(settings.GATEWAY_URL, headers=self._get_headers(), json=payload)
            response.raise_for_status()
            topic_map = [self.get_topic_by_topic_id(topic) for topic in topic_ids]
            response_json = response.json().get("data", {}).get("aggregations", {}).get("data")
            return self.refactor_result(response_json, topic_map, from_date, to_date)
        except requests.RequestException as e:
            raise APIRequestException(detail=f"Failed to fetch sentiment aggregation: {str(e)}")
        except (ValueError, KeyError) as e:
            raise InvalidResponseException(detail=f"Invalid response structure: {str(e)}")

    def fetch_user_projects(self) -> Dict:
        payload = {
            "query": """
                query me {
                    me {
                        status
                        message
                        data {
                            _id
                            username
                            firstName
                            lastName
                            email
                            phone
                            avatar
                            permissions { roles group }
                            projects {
                                _id
                                name
                                displayName
                                defaultTopicId
                                topics { _id name }
                                groupTreeLabels { _id name path }
                            }
                            status
                        }
                    }
                }
            """,
            "variables": {},
        }

        try:
            response = requests.post(settings.CMS_GATEWAY_URL, headers=self._get_headers(), json=payload)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise APIRequestException(detail=f"Failed to fetch user projects: {str(e)}")
        except ValueError as e:
            raise InvalidResponseException(detail=f"Invalid response structure: {str(e)}")

    def get_label_ids_by_topic_id(self, topic_id: str) -> Optional[List[str]]:
        try:
            response_data = self.fetch_user_projects()
            projects = response_data["data"]["me"]["data"]["projects"]

            for project in projects:
                for topic in project["topics"]:
                    if topic["_id"] == topic_id:
                        return self._get_unique_label_ids(project["groupTreeLabels"])
            return None
        except (KeyError, ValueError) as e:
            raise InvalidResponseException(detail=f"Invalid response structure: {str(e)}")

    def _get_unique_label_ids(self, group_tree_labels: List[List[Dict]]) -> List[str]:
        unique_ids = set()
        for sub_array in group_tree_labels:
            for item in sub_array:
                unique_ids.add(item["_id"])
        label_ids = list(unique_ids)
        label_ids.insert(0, "-1")
        return label_ids

    def get_topic_by_topic_id(self, topic_id: str) -> Optional[Dict]:
        try:
            response_data = self.fetch_user_projects()
            projects = response_data["data"]["me"]["data"]["projects"]

            for project in projects:
                for topic in project["topics"]:
                    if topic["_id"] == topic_id:
                        return topic
            return None
        except (KeyError, ValueError) as e:
            raise InvalidResponseException(detail=f"Invalid response structure: {str(e)}")

    def get_sentiment_breakdown_competitor(self, topic_ids: [str], from_date1: str, to_date1: str, from_date2: str, to_date2: str) -> Optional[Dict]:
        if not (self.validate_date_format(from_date1) and self.validate_date_format(to_date1)):
            raise InvalidDateFormatException()
        if not (self.validate_date_format(from_date2) and self.validate_date_format(to_date2)):
            raise InvalidDateFormatException()

        data_preiod_1 = self.get_sentiment_aggregation(topic_ids, from_date1, to_date1)
        data_preiod_2 = self.get_sentiment_aggregation(topic_ids, from_date2, to_date2)
        result = {
            "data_preiod_1": data_preiod_1,
            "data_preiod_2": data_preiod_2,
        }
        return result if data_preiod_1 and data_preiod_2 else {}
