from .main_test import apptest
import pytest
from httpx import AsyncClient

@pytest.mark.anyio
async def test_get_number_of_clients_grouped_by_city():
    async with AsyncClient(app=apptest, base_url="http://localhost:8000") as ac:
        response = await ac.get("/stats/country/", params={"username":"nann","collection":"users_logs","country_name":"France"})    
    assert response.status_code == 404