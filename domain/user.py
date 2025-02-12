from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

class User(BaseModel):
    reference_id: UUID
    name: str
    created_date: datetime

    def to_dict(self):
        return {
            "reference_id": str(self.reference_id),
            "name": self.name,
            "created_date": self.created_date.isoformat()
        }