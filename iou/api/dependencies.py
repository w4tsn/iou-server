from iou.db.db_interface import IouDBInterface
from iou.db.mock_db import MockDB


def get_db() -> IouDBInterface:
    return MockDB.instance()
