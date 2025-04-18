from app.services.sb_api_service import APISentimentAggregationService
from app.services.sb_insight_service import SentimentBreakdownInsightService

import asyncio

if __name__ == "__main__":
    async def main():
        service = SentimentBreakdownInsightService(
            x_refresh_token="Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJfaWQiOiI2NzIzMzdmMWUzZTBmODBkMDUxNzQyNDQiLCJ1c2VybmFtZSI6ImtoYW5oaHV5ZW4iLCJwZXJtaXNzaW9ucyI6Ilt7XCJyb2xlc1wiOltcImFkbWluXCJdLFwiX2lkXCI6XCI2NzRmZDE0NmEyM2QxYzBlMjEyMDgyNmRcIixcImdyb3VwXCI6XCJjb25zdWx0aW5nXCJ9LHtcInJvbGVzXCI6W1wiYWRtaW5cIl0sXCJfaWRcIjpcIjY3NGZkMTQ2YTIzZDFjMGUyMTIwODI2ZVwiLFwiZ3JvdXBcIjpcInNtY2NcIn1dIiwic3RhdHVzIjoiYWN0aXZlIiwiaWF0IjoxNzQ0ODY0NTAxLCJleHAiOjE3NDQ5NTA5MDF9.CEJirATAWu0WHPPSoA7-jsFGi4zUd4dkUrJQ0ztZHfI",
            x_token="Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJfaWQiOiI2NzIzMzdmMWUzZTBmODBkMDUxNzQyNDQiLCJ1c2VybmFtZSI6ImtoYW5oaHV5ZW4iLCJwZXJtaXNzaW9ucyI6Ilt7XCJyb2xlc1wiOltcImFkbWluXCJdLFwiX2lkXCI6XCI2NzRmZDE0NmEyM2QxYzBlMjEyMDgyNmRcIixcImdyb3VwXCI6XCJjb25zdWx0aW5nXCJ9LHtcInJvbGVzXCI6W1wiYWRtaW5cIl0sXCJfaWRcIjpcIjY3NGZkMTQ2YTIzZDFjMGUyMTIwODI2ZVwiLFwiZ3JvdXBcIjpcInNtY2NcIn1dIiwic3RhdHVzIjoiYWN0aXZlIiwiaWF0IjoxNzQ0ODY0NTAxLCJleHAiOjE3NDQ4OTMzMDF9.TU79xLBIntW1gU0lRlUeAU9VKy0GOLTFW4wV4-lN1OM"
        )
        result = await service.generate_insight(
            topic_ids=[
                "5cd2a99d2e81050a12e5339a",
                "5cd19f472e81050a12e50fec",
                "5ddb5034e812840d7850cd7c",
                "5cd1b7e82e81050a12e51125"
            ],
            from_date1="2025-04-14T00:00",
            to_date1="2025-04-16T11:58",
            from_date2="2025-04-07T00:00",
            to_date2="2025-04-13T11:58"
        )
        print(result)

    asyncio.run(main())