import datetime
import uuid
from unittest.mock import patch, MagicMock

import pytest

from domain.transfer_type import TransferType
from exception.amount import AmountNotPositiveException
from exception.fund import FundNotFoundException
from exception.shares import NotEnoughSharesException
from exception.user import SendingUserNotProvidedException, UserNotFoundException, SendingAndReceivingUserSameException
from managers.fund_manager import FundManager
from resources.postgres import PostgreSQL

pytestmark = pytest.mark.asyncio



test_funds_manager = FundManager(PostgreSQL())

@patch('resources.postgres.PostgreSQL.execute_one')
def test_get_fund_available_shares(execute_one):
    execute_one.return_value = [5000]
    shares = test_funds_manager.get_fund_available_shares(uuid.uuid4())
    assert shares == 5000
    execute_one.return_value = None
    shares = test_funds_manager.get_fund_available_shares(uuid.uuid4())
    assert shares == 0

@patch('resources.postgres.PostgreSQL.execute_many')
def test_get_funds(execute_many):
    execute_many.return_value = [[str(uuid.uuid4()), "test", 1000, 500, datetime.datetime.now()],
                                 [str(uuid.uuid4()), "test2", 5000, 2500, datetime.datetime.now()]]
    funds = test_funds_manager.get_funds()
    assert funds[0]['total_shares'] == 1000
    assert funds[0]['name'] == "test"
    assert funds[1]['total_shares'] == 5000
    assert funds[1]['name'] == "test2"

@patch('resources.postgres.PostgreSQL.execute_many')
def test_get_user(execute_many):
    execute_many.return_value = [[str(uuid.uuid4()), "test", datetime.datetime.now()],
                                 [str(uuid.uuid4()), "test2", datetime.datetime.now()]]
    users = test_funds_manager.get_users()
    assert users[0]['name'] == "test"
    assert users[1]['name'] == "test2"

@patch('resources.postgres.PostgreSQL.execute_many')
@patch('resources.postgres.PostgreSQL.exists')
def test_cap_table(exists, execute_many):
    execute_many.return_value = [[str(uuid.uuid4()), str(uuid.uuid4()), 10000, datetime.datetime.now()],
                                 [str(uuid.uuid4()), str(uuid.uuid4()), 50000, datetime.datetime.now()]]
    exists.return_value = False
    with pytest.raises(FundNotFoundException):
        test_funds_manager.get_cap_table(str(uuid.uuid4()))
    exists.return_value = True
    cap_tables = test_funds_manager.get_cap_table(str(uuid.uuid4()))
    assert cap_tables[0]['total_shares'] == 10000
    assert cap_tables[1]['total_shares'] == 50000

@patch('resources.postgres.PostgreSQL.execute_one')
def test_get_user_shares(execute_one):
    execute_one.return_value = [6000]
    shares = test_funds_manager.get_user_shares(uuid.uuid4(), uuid.uuid4())
    assert shares == 6000
    execute_one.return_value = None
    shares = test_funds_manager.get_user_shares(uuid.uuid4(), uuid.uuid4())
    assert shares == 0

@patch('resources.postgres.PostgreSQL.execute_many')
@patch('resources.postgres.PostgreSQL.exists')
def test_get_transfers(exists, execute_many):
    execute_many.return_value = [[str(uuid.uuid4()), str(uuid.uuid4()), str(uuid.uuid4()), str(uuid.uuid4()),
                                    TransferType.TRANSFER, 5000, datetime.datetime.now()],
                                 [str(uuid.uuid4()), None, str(uuid.uuid4()), str(uuid.uuid4()),
                                    TransferType.GRANT, 60000, datetime.datetime.now()]]
    exists.return_value = False
    with pytest.raises(FundNotFoundException):
        test_funds_manager.get_transfers(str(uuid.uuid4()))
    exists.return_value = True
    transfers = test_funds_manager.get_transfers(str(uuid.uuid4()))
    assert transfers[0]['transfer_type'] == TransferType.TRANSFER
    assert transfers[1]['transfer_type'] == TransferType.GRANT
    assert transfers[0]['amount'] == 5000
    assert transfers[1]['amount'] == 60000


@patch('resources.postgres.PostgreSQL.execute')
@patch('managers.fund_manager.FundManager.verify_user')
@patch('managers.fund_manager.FundManager.verify_fund')
@patch('managers.fund_manager.FundManager.get_user_shares')
@patch('managers.fund_manager.FundManager.get_fund_available_shares')
def test_create_transfer(fund_available_shares, get_user_shares, verify_fund, verify_user, execute):
    get_user_shares.return_value = 10000000
    fund_available_shares.return_value = 10000000
    with pytest.raises(SendingUserNotProvidedException):
        test_funds_manager.create_transfer(uuid.uuid4(), uuid.uuid4(), 50000,
                                           TransferType.TRANSFER)
    test_funds_manager.create_transfer(uuid.uuid4(), uuid.uuid4(), 50000,
                                       TransferType.GRANT)
    verify_user.return_value = False
    with pytest.raises(UserNotFoundException):
        test_funds_manager.create_transfer(uuid.uuid4(), uuid.uuid4(), 50000,
                                           TransferType.TRANSFER, uuid.uuid4())
    verify_user.return_value = True
    verify_fund.return_value = False
    with pytest.raises(FundNotFoundException):
        test_funds_manager.create_transfer(uuid.uuid4(), uuid.uuid4(), 50000,
                                           TransferType.TRANSFER, uuid.uuid4())
    verify_fund.return_value = True
    with pytest.raises(AmountNotPositiveException):
        test_funds_manager.create_transfer(uuid.uuid4(), uuid.uuid4(), -500,
                                           TransferType.TRANSFER, uuid.uuid4())

    with pytest.raises(AmountNotPositiveException):
        test_funds_manager.create_transfer(uuid.uuid4(), uuid.uuid4(), 0,
                                           TransferType.TRANSFER, uuid.uuid4())
    user_uuid = uuid.uuid4()
    with pytest.raises(SendingAndReceivingUserSameException):
        test_funds_manager.create_transfer(user_uuid, uuid.uuid4(), 6000,
                                           TransferType.TRANSFER, user_uuid)

    get_user_shares.return_value = 20
    with pytest.raises(NotEnoughSharesException):
        test_funds_manager.create_transfer(uuid.uuid4(), uuid.uuid4(), 50000,
                                           TransferType.TRANSFER, uuid.uuid4())
    get_user_shares.return_value = 10000000
    fund_available_shares.return_value = 5
    with pytest.raises(NotEnoughSharesException):
        test_funds_manager.create_transfer(uuid.uuid4(), uuid.uuid4(), 50000,
                                           TransferType.GRANT)
    fund_available_shares.return_value = 10000000
    test_funds_manager.create_transfer(uuid.uuid4(), uuid.uuid4(), 50000,
                                       TransferType.TRANSFER, uuid.uuid4())