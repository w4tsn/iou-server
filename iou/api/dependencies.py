from iou.db.db_interface import IouDBInterface
from iou.db.sql_db import SqlDb


def get_db() -> IouDBInterface:
    return SqlDb.instance()
