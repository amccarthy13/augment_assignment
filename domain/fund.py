from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

class Fund(BaseModel):
    reference_id: UUID
    name: str
    total_shares: int
    available_shares: int
    created_date: datetime

    def to_dict(self):
        return {
            "reference_id": str(self.reference_id),
            "name": self.name,
            "total_shares": self.total_shares,
            "available_shares": self.available_shares,
            "created_date": self.created_date.isoformat(),
        }