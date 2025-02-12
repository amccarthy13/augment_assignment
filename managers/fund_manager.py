import logging
from typing import Optional, List
from uuid import UUID

from domain.cap_table import CapTable
from domain.fund import Fund
from domain.transfer import Transfer
from domain.transfer_type import TransferType
from domain.user import User
from exception.amount import AmountNotPositiveException
from exception.fund import FundNotFoundException
from exception.shares import NotEnoughSharesException
from exception.user import SendingAndReceivingUserSameException, SendingUserNotProvidedException, UserNotFoundException
from resources.postgres import PostgreSQL


class FundManager(object):

    def __init__(self, postgres: PostgreSQL):
        self.postgres = postgres


    def add_user(self, name: str) -> None:
        query = "INSERT INTO augment.users (name) VALUES (%s);"
        args = [name]
        self.postgres.execute(query, args)

    def add_fund(self, name: str, total_shares: int) -> None:
        query = "INSERT INTO augment.funds (name, units) VALUES (%s, %s);"
        args = [name, total_shares]
        self.postgres.execute(query, args)

    def get_fund_available_shares(self, fund: UUID) -> int:
        query = "SELECT available_shares FROM augment.available_shares WHERE reference_id = %s;"
        row = self.postgres.execute_one(query, [fund])
        return int(row[0]) if row else 0

    def get_funds(self) -> List[str]:
        query = ("SELECT f.reference_id, f.name, f.units AS total_shares, "
                    "COALESCE(shares.available_shares, f.units) AS available_shares, "
                    "f.created_date FROM augment.funds f LEFT JOIN augment.available_shares shares "
                    "ON shares.reference_id = f.reference_id;")
        rows = self.postgres.execute_many(query)
        funds = []
        for row in rows:
            fund = Fund(reference_id=row[0], name=row[1], total_shares=row[2], available_shares=row[3],
                        created_date=row[4])
            funds.append(fund.to_dict())
        return funds

    def get_users(self) -> List[str]:
        query ="SELECT reference_id, name, created_date FROM augment.users;"
        rows = self.postgres.execute_many(query)
        users = []
        for row in rows:
            user = User(reference_id=row[0], name=row[1], created_date=row[2])
            users.append(user.to_dict())
        return users

    def get_cap_table(self, fund: str) -> List[str]:
        if not self.verify_fund(fund):
            raise FundNotFoundException()
        query = ("SELECT ct.user_id, ct.fund, ct.total_shares, ct.last_update, u.name FROM augment.cap_table ct "
                 "JOIN augment.users u ON u.reference_id = ct.user_id WHERE ct.fund = %s;")
        args = [fund]
        rows = self.postgres.execute_many(query, args)
        cap_tables = []
        for row in rows:
            cap_table = CapTable(user_id=row[0], fund=row[1], total_shares=row[2], last_update=row[3],
                                 username=row[4])
            cap_tables.append(cap_table.to_dict())
        return cap_tables

    def get_user_shares(self, user_id: UUID, fund: UUID) -> int:
        query = "SELECT total_shares FROM augment.cap_table WHERE user_id = %s AND fund = %s;"
        args = [user_id, fund]
        row = self.postgres.execute_one(query, args)
        return int(row[0]) if row else 0

    def get_transfers(self, fund: str) -> List[str]:
        if not self.verify_fund(fund):
            raise FundNotFoundException()
        query = ("SELECT t.reference_id, t.sending_user, t.receiving_user, t.fund, t.transfer_type, t.amount, "
                 "t.created_date, su.name AS sending_username, ru.name AS receiving_username "
                 "FROM augment.transfers t "
                 "LEFT JOIN augment.users su ON su.reference_id = t.sending_user "
                 "JOIN augment.users ru ON ru.reference_id = t.receiving_user "
                 "WHERE t.fund = %s ORDER BY t.created_date DESC;")
        args = [fund]
        rows = self.postgres.execute_many(query, args)
        transfers = []
        for row in rows:
            transfer = Transfer(reference_id=row[0], sending_user=row[1], receiving_user=row[2],
                                fund=row[3], transfer_type=row[4], amount=row[5], created_date=row[6],
                                sending_username=row[7], receiving_username=row[8])
            transfers.append(transfer.to_dict())
        return transfers

    def verify_user(self, receiving_user: UUID) -> bool:
        query = "SELECT EXISTS(SELECT 1 FROM augment.users WHERE reference_id = %s);"
        args = [receiving_user]
        return self.postgres.exists(query, args)

    def verify_fund(self, fund: UUID) -> bool:
        query = "SELECT EXISTS(SELECT 1 FROM augment.funds WHERE reference_id = %s);"
        args = [fund]
        return self.postgres.exists(query, args)


    def create_transfer(self, receiving_user: UUID, fund: UUID, amount: int,
                 transfer_type: TransferType, sending_user: Optional[UUID] = None) -> None:
        if transfer_type == TransferType.TRANSFER and sending_user is None:
            raise SendingUserNotProvidedException()

        if not self.verify_user(receiving_user) or (not self.verify_user(sending_user) if sending_user else False):
            raise UserNotFoundException()
        if not self.verify_fund(fund):
            raise FundNotFoundException()
        if amount <= 0:
            raise AmountNotPositiveException()
        if receiving_user == sending_user:
            raise SendingAndReceivingUserSameException()
        if transfer_type == TransferType.TRANSFER:
            total_shares = self.get_user_shares(sending_user, fund)
            if total_shares < amount:
                raise NotEnoughSharesException()
        else:
            available_shares = self.get_fund_available_shares(fund)
            if available_shares < amount:
                raise NotEnoughSharesException()

        query = ("INSERT INTO augment.transfers (receiving_user, sending_user, fund, amount, transfer_type) "
                 "VALUES (%s, %s, %s, %s, %s);")
        args = [receiving_user, sending_user, fund, amount, transfer_type]
        self.postgres.execute(query, args)


