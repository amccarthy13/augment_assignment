from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

class CapTable(BaseModel):
    user_id: UUID
    username: str
    fund: UUID
    total_shares: int
    last_update: datetime

    def to_dict(self):
        return {
            "user_id": str(self.user_id),
            "username" : self.username,
            "fund": str(self.fund),
            "total_shares": self.total_shares,
            "last_update": self.last_update.isoformat(),
        }