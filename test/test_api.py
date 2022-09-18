import json
from abc import ABC, abstractmethod
from datetime import datetime

import pytest
from httpx import AsyncClient

from iou.db.db_interface import IouDBInterface
from iou.lib.group import NamedGroup
from iou.lib.id import ID
from iou.lib.user import User


class AbstractTestAPI(ABC):

    database: IouDBInterface

    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.create_db()
        self.initialize_db()

    @abstractmethod
    def create_db(self) -> None:
        pass

    def initialize_db(self) -> None:
        self.database.add_user(
            User(user_id="alex", name="Alex", email="alex@example.com")
        )
        self.database.add_user(
            User(user_id="victor", name="Victor", email="victor@example.com")
        )

        self.database.add_group(
            NamedGroup(group_id=ID("group"), users=self.database.get_users())
        )

    @pytest.mark.asyncio
    async def test_create_user(self, iou_client: AsyncClient) -> None:
        response = await iou_client.post(
            "/api/v1/users",
            headers={"content-type": "application/json"},
            content=json.dumps({"name": "Dr. Evil", "email": "evil@example.com"}),
        )
        assert response.status_code == 200, response.json()
        assert response.json()["name"] == "Dr. Evil"
        assert isinstance(response.json()["user_id"], str)
        assert self.database.get_user(response.json()["user_id"]) == User(
            **response.json()
        )

    @pytest.mark.asyncio
    async def test_create_group(self, iou_client: AsyncClient) -> None:
        response = await iou_client.post(
            "/api/v1/groups",
            headers={"content-type": "application/json"},
            content=json.dumps({"name": "My group"}),
        )
        assert response.status_code == 200, response.json()
        assert response.json()["name"] == "My group"

    @pytest.mark.asyncio
    async def test_create_group_transaction(self, iou_client: AsyncClient) -> None:
        transaction = {
            "split_type": "equal",
            "date": str(datetime(2022, 1, 1)),
            "deposits": {"alex": 420},
            "split_parameters": {"victor": 0, "alex": 0},
        }
        response = await iou_client.post(
            "/api/v1/groups/group/transactions",
            headers={"content-type": "application/json"},
            content=json.dumps(transaction),
        )
        assert response.status_code == 200, response.json()
        response_body = response.json()
        assert response_body["split_type"] == "equal"
        assert response_body["deposits"] == {"alex": 420}
        assert response_body["withdrawals"] == {"victor": 210, "alex": 210}

    @pytest.mark.asyncio
    async def test_group_balances(self, iou_client: AsyncClient) -> None:
        response = await iou_client.get(
            "/api/v1/groups/group/balances",
            headers={"content-type": "application/json"},
        )
        assert response.status_code == 200, response.json()
        response_body = response.json()
        assert response_body["alex"] == 0

    @pytest.mark.asyncio
    async def test_group_user_balance(self, iou_client: AsyncClient) -> None:
        response = await iou_client.get(
            "/api/v1/groups/group/balances/alex",
            headers={"content-type": "application/json"},
        )
        assert response.status_code == 200, response.json()
        assert response.json() == 0


class TestAPIMockDB(AbstractTestAPI):
    def create_db(self) -> None:
        # pylint: disable=import-outside-toplevel
        from iou.db.mock_db import MockDB

        self.database = MockDB.instance()
