import json
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, Generator

import pytest
from httpx import AsyncClient

from iou.api.dependencies import get_db
from iou.db.db_interface import IouDBInterface
from iou.lib.group import NamedGroup
from iou.lib.id import ID
from iou.lib.user import User
from iou.main import app


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

    async def _test_transaction_create_request(
        self, iou_client: AsyncClient, body: Dict[str, Any], expected: Dict[str, Any]
    ) -> None:
        """Make a transaction create request"""
        response = await iou_client.post(
            "/api/v1/groups/group/transactions",
            headers={
                "content-type": "application/json",
                "x-iou-pre-authenticated": "test-user",
            },
            content=json.dumps(body),
        )
        assert response.status_code == 200, response.text
        response_body = response.json()
        assert response_body["split_type"] == expected["split_type"]
        assert response_body["deposits"] == expected["deposits"]
        assert response_body["withdrawals"] == expected["withdrawals"]

    @pytest.mark.asyncio
    async def test_create_user(self, iou_client: AsyncClient) -> None:
        response = await iou_client.post(
            "/api/v1/users",
            headers={
                "content-type": "application/json",
                "x-iou-pre-authenticated": "test-user",
            },
            content=json.dumps({"name": "Dr. Evil", "email": "evil@example.com"}),
        )
        assert response.status_code == 200, response.json()
        assert response.json()["name"] == "Dr. Evil"
        assert isinstance(response.json()["user_id"], str)
        assert self.database.get_user(response.json()["user_id"]) == User(
            **response.json()
        ), response.json()

    @pytest.mark.asyncio
    async def test_create_group(self, iou_client: AsyncClient) -> None:
        response = await iou_client.post(
            "/api/v1/groups",
            headers={
                "content-type": "application/json",
                "x-iou-pre-authenticated": "test-user",
            },
            content=json.dumps({"name": "My group"}),
        )
        assert response.status_code == 200, response.json()
        assert response.json()["name"] == "My group"

    @pytest.mark.asyncio
    async def test_create_group_transaction_equal(
        self, iou_client: AsyncClient
    ) -> None:
        await self._test_transaction_create_request(
            iou_client,
            body={
                "split_type": "equal",
                "date": str(datetime(2022, 1, 1)),
                "deposits": {"alex": 420},
                "split_parameters": {"victor": 0, "alex": 0},
            },
            expected={
                "split_type": "equal",
                "deposits": {"alex": 420},
                "withdrawals": {"victor": 210, "alex": 210},
            },
        )

    @pytest.mark.asyncio
    async def test_create_group_transaction_by_share(
        self, iou_client: AsyncClient
    ) -> None:
        await self._test_transaction_create_request(
            iou_client,
            body={
                "split_type": "by_share",
                "date": str(datetime(2022, 1, 1)),
                "deposits": {"alex": 100},
                "split_parameters": {"victor": 4, "alex": 6},
            },
            expected={
                "split_type": "by_share",
                "deposits": {"alex": 100},
                "withdrawals": {"victor": 40, "alex": 60},
            },
        )

    @pytest.mark.asyncio
    async def test_create_group_transaction_by_percentage(
        self, iou_client: AsyncClient
    ) -> None:
        await self._test_transaction_create_request(
            iou_client,
            body={
                "split_type": "by_percentage",
                "date": str(datetime(2022, 1, 1)),
                "deposits": {"alex": 300},
                "split_parameters": {"victor": 33, "alex": 67},
            },
            expected={
                "split_type": "by_percentage",
                "deposits": {"alex": 300},
                "withdrawals": {
                    "victor": pytest.approx(100, rel=1e-2),
                    "alex": pytest.approx(200, rel=1e-2),
                },
            },
        )

    @pytest.mark.asyncio
    async def test_create_group_transaction_invalid_split(
        self, iou_client: AsyncClient
    ) -> None:
        with pytest.raises(AssertionError):
            await self._test_transaction_create_request(
                iou_client,
                body={
                    "split_type": "by_percentage",
                    "date": str(datetime(2022, 1, 1)),
                    "deposits": {"alex": 300},
                    "split_parameters": {"victor": 20, "alex": 60},
                },
                expected={
                    "split_type": "by_percentage",
                    "deposits": {"alex": 300},
                    "withdrawals": {
                        "victor": pytest.approx(100, rel=1e-2),
                        "alex": pytest.approx(200, rel=1e-2),
                    },
                },
            )

    @pytest.mark.asyncio
    async def test_create_group_transaction_by_adjustment(
        self, iou_client: AsyncClient
    ) -> None:
        await self._test_transaction_create_request(
            iou_client,
            body={
                "split_type": "by_adjustment",
                "date": str(datetime(2022, 1, 1)),
                "deposits": {"alex": 200},
                "split_parameters": {"victor": 0, "alex": 100},
            },
            expected={
                "split_type": "by_adjustment",
                "deposits": {"alex": 200},
                "withdrawals": {"victor": 50, "alex": 150},
            },
        )

    @pytest.mark.asyncio
    async def test_create_group_transaction_unequal(
        self, iou_client: AsyncClient
    ) -> None:
        await self._test_transaction_create_request(
            iou_client,
            body={
                "split_type": "unequal",
                "date": str(datetime(2022, 1, 1)),
                "deposits": {"alex": 200},
                "split_parameters": {"victor": 50, "alex": 150},
            },
            expected={
                "split_type": "unequal",
                "deposits": {"alex": 200},
                "withdrawals": {"victor": 50, "alex": 150},
            },
        )

    @pytest.mark.asyncio
    async def test_group_balances(self, iou_client: AsyncClient) -> None:
        response = await iou_client.get(
            "/api/v1/groups/group/balances",
            headers={
                "content-type": "application/json",
                "x-iou-pre-authenticated": "test-user",
            },
        )
        assert response.status_code == 200, response.json()
        response_body = response.json()
        assert response_body["alex"] == 0

    @pytest.mark.asyncio
    async def test_group_user_balance(self, iou_client: AsyncClient) -> None:
        response = await iou_client.get(
            "/api/v1/groups/group/balances/alex",
            headers={
                "content-type": "application/json",
                "x-iou-pre-authenticated": "test-user",
            },
        )
        assert response.status_code == 200, response.json()
        assert response.json() == 0


class TestAPIMockDB(AbstractTestAPI):
    @pytest.fixture(autouse=True)
    def use_mock_db(self) -> Generator[None, None, None]:
        # Only initialize db within the context of this method
        # pylint: disable=import-outside-toplevel
        from iou.db.mock_db import MockDB

        app.dependency_overrides[get_db] = MockDB.instance
        yield
        app.dependency_overrides = {}

    def create_db(self) -> None:
        # pylint: disable=import-outside-toplevel
        from iou.db.mock_db import MockDB

        self.database = MockDB.instance()


class TestAPISqlDB(AbstractTestAPI):
    @pytest.fixture(scope="session", autouse=True)
    def cleanup_db(self) -> None:
        # Only initialize db within the context of this method
        # pylint: disable=import-outside-toplevel
        from iou.db.sql_db import dispose_database_tables

        dispose_database_tables()

    @pytest.fixture(scope="function", autouse=True)
    def init(self) -> Generator[None, None, None]:
        # Only initialize db within the context of this method
        # pylint: disable=import-outside-toplevel
        from iou.db.sql_db import dispose_database_tables, init_database_tables

        init_database_tables()
        yield
        dispose_database_tables()

    def create_db(self) -> None:
        # Only initialize db within the context of this method
        # pylint: disable=import-outside-toplevel
        from iou.db.sql_db import SqlDb

        self.database = SqlDb.instance()
