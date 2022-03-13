from __future__ import annotations

import uuid


class ID(str):
    
    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(
            title = 'ID',
            description = 'ID that uniquely identifies an iou entity'
        )

    @classmethod
    def generate(cls) -> ID:
        return cls(uuid.uuid4())
