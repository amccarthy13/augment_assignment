from flask import request, jsonify

from AugmentApp import AugmentApp
from domain.transfer_type import TransferType
from exception.amount import AmountNotPositiveException
from exception.fund import FundNotFoundException
from exception.shares import NotEnoughSharesException
from exception.user import SendingAndReceivingUserSameException, SendingUserNotProvidedException, UserNotFoundException
from managers.fund_manager import FundManager

app = AugmentApp("augment_app")

@app.route('/user', methods=['POST'])
def add_user():
    manager = FundManager(app.postgres)
    name = request.args.get('name')
    if not name:
        return jsonify({"message": "missing required 'name' parameter"}), 400
    try:
        manager.add_user(name)
        return jsonify({"message": "user created successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/fund', methods=['POST'])
def add_fund():
    manager = FundManager(app.postgres)
    name = request.args.get('name')
    total_shares = request.args.get('total_shares')
    if not name:
        return jsonify({"message": "missing required 'name' parameter"}), 400
    if not total_shares:
        return jsonify({"message": "missing required 'total_shares' parameter"}), 400

    try:
        manager.add_fund(name, int(total_shares))
        return jsonify({"message": "fund created successfully"}), 201
    except ValueError:
        return jsonify({"message": "invalid format for parameter(s)"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/users', methods=['GET'])
def get_users():
    try:
        manager = FundManager(app.postgres)
        users = manager.get_users()
        return jsonify({"users": users}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/funds', methods=['GET'])
def get_funds():
    try:
        manager = FundManager(app.postgres)
        funds = manager.get_funds()
        return jsonify({"funds": funds}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/cap_table', methods=['GET'])
def get_cap_table():
    fund = request.args.get('fund')
    if not fund:
        return jsonify({"message": "missing required 'fund' parameter"}), 400
    try:
        manager = FundManager(app.postgres)
        funds = manager.get_cap_table(fund)
        return jsonify({"cap_table": funds}), 200
    except FundNotFoundException:
        return jsonify({"message": "fund not found"}), 404
    except ValueError:
        return jsonify({"message": "invalid format for parameter(s)"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/transfers', methods=['GET'])
def get_transfers():
    fund = request.args.get('fund')
    if not fund:
        return jsonify({"message": "missing required 'fund' parameter"}), 400
    try:
        manager = FundManager(app.postgres)
        funds = manager.get_transfers(fund)
        return jsonify({"transfers": funds}), 200
    except FundNotFoundException:
        return jsonify({"message": "fund not found"}), 404
    except ValueError:
        return jsonify({"message": "invalid format for parameter(s)"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/transfer', methods=['POST'])
def create_transfer():
    manager = FundManager(app.postgres)
    data = request.get_json()
    if not data:
        return jsonify({"error": "invalid request"}), 400
    sending_user = data.get('sending_user')
    receiving_user = data.get('receiving_user')
    fund = data.get('fund')
    amount = data.get('amount')
    transfer_type = data.get('transfer_type')
    if not (receiving_user or fund or amount or transfer_type):
        return jsonify({"error": "not all required parameters provided"}), 400
    try:
        manager.create_transfer(receiving_user, fund, int(amount), TransferType(transfer_type), sending_user)
        return jsonify({"message": "transfer created successfully"}), 201
    except AmountNotPositiveException:
        return jsonify({"message": "Amount must be greater than 0."}), 400
    except SendingAndReceivingUserSameException:
        return jsonify({"message": "Sending and receiving user cannot be the same"}), 400
    except SendingUserNotProvidedException:
        return jsonify({"message": "Sending user must be provided for transfers"}), 400
    except NotEnoughSharesException:
        return jsonify({"message": "Not enough shares to perform transaction"}), 400
    except UserNotFoundException:
        return jsonify({"message": "user not found"}), 404
    except FundNotFoundException:
        return jsonify({"message": "fund not found"}), 404
    except ValueError:
        return jsonify({"message": "invalid format for parameter(s)"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.set_postgres()
    app.run(port=8000, debug=True)
