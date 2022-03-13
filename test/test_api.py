import json
from abc import abstractmethod, ABC

import iou
from fastapi.testclient import TestClient
from iou.db.db_interface import IouDBInterface
from pytest import fixture

from datetime import datetime


class AbstractTestAPI(ABC):

    client : TestClient
    db : IouDBInterface

    @fixture(autouse=True)
    def setup(self) -> None:
        from iou.main import app
        self.client = TestClient(app)
        self.create_db()
        self.initialize_db()

    @abstractmethod
    def create_db(self) -> None:
        pass

    def initialize_db(self) -> None:
        self.db.add_user(iou.lib.user.User(user_id='alex', name='Alex', email='alex@example.com'))
        self.db.add_user(iou.lib.user.User(user_id='victor', name='Victor', email='victor@example.com'))
        
        self.db.add_group(iou.lib.group.Group(group_id='group', users=self.db.get_users()))


    def test_create_user(self):
        response = self.client.post('/api/v1/users', headers={'content-type': 'application/json'}, data=json.dumps({'name': 'Dr. Evil', 'email': 'evil@example.com'}))
        assert response.status_code == 200, response.json()
        assert response.json()['name'] == 'Dr. Evil'
        assert isinstance(response.json()['user_id'], str)
        assert self.db.get_user(response.json()['user_id']) == iou.lib.user.User(**response.json())

    def test_create_group(self):
        response = self.client.post('/api/v1/groups', headers={'content-type': 'application/json'}, data=json.dumps({'name': 'My group'}))
        assert response.status_code == 200, response.json()
        assert response.json()['name'] == 'My group'

    def test_create_group_transaction(self):
        transaction = {
            'split_type': 'equal',
            'date': str(datetime(2022, 1, 1)),
            'deposits': { 'alex': 420 },
            'split_parameters': { 'victor': 0, 'alex': 0 }
        }
        response = self.client.post('/api/v1/groups/group/transactions', headers={'content-type': 'application/json'}, data=json.dumps(transaction))
        assert response.status_code == 200, response.json()
        response_body = response.json()
        assert response_body['split_type'] == 'equal'
        assert response_body['deposits'] == {'alex': 420}
        assert response_body['withdrawals'] == {'victor': 210, 'alex': 210}

    def test_group_balances(self):
        response = self.client.get('/api/v1/groups/group/balances', headers={'content-type': 'application/json'})
        assert response.status_code == 200, response.json()
        response_body = response.json()
        assert response_body['alex'] == 0

    def test_group_user_balance(self):
        response = self.client.get('/api/v1/groups/group/balances/alex', headers={'content-type': 'application/json'})
        assert response.status_code == 200, response.json()
        assert response.json() == 0

class TestAPIMockDB(AbstractTestAPI):

    def create_db(self):
        from iou.db.mock_db import MockDB
        self.db = MockDB.instance()
        
       