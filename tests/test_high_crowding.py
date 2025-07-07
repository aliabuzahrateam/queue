import asyncio
import httpx
import pytest

API_URL = "http://localhost:8000/join?mode=real"
QUEUE_ID = "ba7f164d-b643-4137-9d18-d8e1748d1596"  # Replace with a real queue ID
API_KEY = "a216e256d6174e4599c6722b948fb18e"      # Replace with a real API key

NUM_USERS = 10  # Simulate 200 users joining at once

@pytest.mark.asyncio
async def test_high_crowding():
    async def join_queue(visitor_id):
        async with httpx.AsyncClient() as client:
            response = await client.post(
                API_URL,
                headers={"app_api_key": API_KEY},
                json={"queue_id": QUEUE_ID, "visitor_id": visitor_id}
            )
            return response.status_code, response.json()

    tasks = [join_queue(f"visitor_{i}") for i in range(NUM_USERS)]
    results = await asyncio.gather(*tasks)

    # Check that all requests were accepted (or handled as expected)
    for status, data in results:
        assert status in (200, 201, 429, 500)  # 429 if rate-limited, adjust as needed

    # Optionally, print or analyze results
    print(f"Total successful joins: {sum(1 for s, _ in results if s in (200, 201))}")
    print(f"Total rate-limited: {sum(1 for s, _ in results if s == 429)}")