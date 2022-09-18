from __future__ import annotations

import uuid
from typing import Any


class ID(str):
    @classmethod
    def __modify_schema__(cls, field_schema: Any) -> None:
        field_schema.update(
            title="ID", description="ID that uniquely identifies an iou entity"
        )

    @classmethod
    def generate(cls) -> ID:
        return cls(uuid.uuid4())
