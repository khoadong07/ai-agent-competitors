import requests
from typing import Dict, List, Optional
from datetime import datetime
from openai import OpenAI
from app.core.config import settings
from app.core.exceptions import APIRequestException, InvalidResponseException, DateRangeException, \
    InvalidDateFormatException


class APISovService:
    def __init__(self, x_token: str, x_refresh_token: str):
        self.x_token = x_token
        self.x_refresh_token = x_refresh_token
        self.openai_client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=settings.OPENROUTER_API_KEY,
        )

    def _get_headers(self) -> Dict[str, str]:
        return {
            "accept": "application/graphql-response+json, application/json",
            "content-type": "application/json",
            "origin": "https://live.kompa.ai",
            "referer": "https://live.kompa.ai/",
            "user-agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"
            ),
            "x-refresh-token": self.x_refresh_token,
            "x-token": self.x_token,
        }

    def validate_date_format(self, date_str: str) -> bool:
        try:
            datetime.strptime(date_str, "%Y-%m-%dT%H:%M")
            return True
        except ValueError:
            return False

    def get_sov_data(self, topic_ids: List[str], from_date: str, to_date: str) -> Optional[Dict]:
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
                "aggs": [{"type": "TERMS", "extendName": "BUZZ_TRENDLINE_GLOBAL", "field": "INDEX"}],
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
                    "sentiments": ["NONE", "POSITIVE", "NEGATIVE", "NEUTRAL"],
                    "labels": self.get_label_ids_by_topic_id(topic_ids[0]),
                    "levels": ["NONE", "LEVEL_1", "LEVEL_2", "LEVEL_3"],
                },
            },
        }

        try:
            response = requests.post(settings.GATEWAY_URL, headers=self._get_headers(), json=payload)
            response.raise_for_status()
            data = response.json().get("data", {}).get("aggregations", {}).get("data")
            return data
        except requests.RequestException as e:
            raise APIRequestException(detail=f"Failed to fetch SOV data: {str(e)}")
        except (ValueError, KeyError) as e:
            raise InvalidResponseException(detail=f"Invalid response structure: {str(e)}")

    def get_buzz_data(self, topic_id: str, from_date: str, to_date: str) -> Optional[Dict]:
        payload = {
            "query": """
                query buzzes($input: IndexesInput!, $filter: FilterBuzzInput) {
                    buzzes(input: $input, filter: $filter) {
                        status
                        message
                        total
                        skip
                        limit
                        data {
                            _id
                            _index
                            _source {
                                type
                                publishedDate
                                siteId
                                siteName
                                url
                                title
                                content
                                interactions
                                parentId
                                parentDate
                                commentParentId
                                sentiment { value createdAt createdBy updatedAt updatedBy }
                                labels { value createdAt createdBy }
                                profile { id name }
                            }
                        }
                    }
                }
            """,
            "variables": {
                "input": {"indexes": [topic_id]},
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
                    ],
                    "isDeleted": False,
                    "labels": self.get_label_ids_by_topic_id(topic_id),
                    "sentiments": ["NEGATIVE", "POSITIVE", "NEUTRAL"],
                    "levels": ["NONE", "LEVEL_1", "LEVEL_2", "LEVEL_3"],
                    "skip": 0,
                    "limit": 100,
                },
            },
        }

        try:
            response = requests.post(settings.GATEWAY_URL, headers=self._get_headers(), json=payload)
            response.raise_for_status()
            data = response.json()["data"]["buzzes"]["data"]
            sorted_data = sorted(data, key=lambda x: int(x["_source"].get("interactions", 0)), reverse=True)[:2]
            return {"topic_id": topic_id, "top_interactions_data": sorted_data}
        except requests.RequestException as e:
            raise APIRequestException(detail=f"Failed to fetch buzz data: {str(e)}")
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

