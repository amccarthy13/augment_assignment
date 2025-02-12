from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from domain.transfer_type import TransferType


class Transfer(BaseModel):
    reference_id: UUID
    sending_user: Optional[UUID]
    receiving_user: UUID
    fund: UUID
    transfer_type: TransferType
    amount: int
    created_date: datetime
    sending_username: Optional[str]
    receiving_username: str

    def to_dict(self):
        return {
            "reference_id": str(self.reference_id),
            "sending_user": str(self.sending_user) if self.sending_user else None,
            "receiving_user": str(self.receiving_user),
            "fund": str(self.fund),
            "transfer_type": self.transfer_type.value,
            "amount": self.amount,
            "created_date": self.created_date.isoformat(),
            "sending_username": self.sending_username,
            "receiving_username": self.receiving_username,
        }