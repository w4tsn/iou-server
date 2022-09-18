from datetime import datetime

from iou.lib.group import Group
from iou.lib.split import ByPercentageSplitStrategy, EqualSplitStrategy
from iou.lib.transaction import PartialTransaction, Transaction
from iou.lib.user import User

# Create some users
u1 = User(user_id="1", name="Victor", email="victor@example.com")
u2 = User(user_id="2", name="Alex", email="alex@example.com")
u3 = User(user_id="3", name="Dr. Evil", email="evil@example.com")

# Create a group for shared expenses. Users can either be passed to the constructor..
g = Group(group_id="1", users=[u1])

# ..or added later on.
g.add_user_with_backreference(u2)

# Create some deposits for our first transaction
# For readability, PartialTransactions can be passed as dictionaries
deposits = [
    PartialTransaction(user=u1, amount=2000),
    {"user": u2, "amount": 5000},
]

# Define the strategy for distributing the expenses to the users
split = ByPercentageSplitStrategy(deposits=deposits, split_parameters={u1: 80, u2: 20})

# Create a transaction with the deposits and withdrawals (calculated using the above split strategy)
t1 = Transaction(
    split_type=split.split_type,
    deposits=deposits,
    withdrawals=split.compute_split(),
    date=datetime.now(),
)

# Add the transaction to our group
g.add_transaction(t1)

# Create another transaction
deposits = [{"user": u1, "amount": 4200}]
split = EqualSplitStrategy(deposits=deposits, split_parameters={u2: 0})

# Provide a split object directly instead of manually passing split_type and withdrawals. Date is also optional.
t2 = Transaction(deposits=deposits, split=split)
g.add_transaction(t2)

# Query the balances for all users of a group..
print(g.balances())

# ..or for a single user of a group..
print(g.balance_for(u1))

# ..or the user's total balance across all groups
print(u2.balance())

# Quick test that a user mismatch between transaction and group is detected
try:
    g.add_transaction(Transaction(deposits=[{"user": u3, "amount": 1000}], split=split))
except AssertionError as e:
    assert str(e) == "User mismatch between group and transaction"
