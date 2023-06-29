import pytest
from httpx import AsyncClient
from .test_config import BASE_URL

@pytest.mark.anyio
async def test_get_number_of_clients_grouped_by_city():
    async with AsyncClient(base_url=BASE_URL) as ac:
        response = await ac.get("/stats/country/", params={"username":"nann","collection":"users_logs","country_name":"France"})
    assert response.status_code == 200