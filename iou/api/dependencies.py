from ..db.mock_db import MockDB

def get_db():
    return MockDB.instance()