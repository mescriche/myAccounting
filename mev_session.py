import os
from datamodel import UserData, AccountsTree
from dbase import db_open, Session, Account, Transaction, BookEntry
from sqlalchemy import select
root = os.getcwd()
user = UserData(root, 'mev')
db_open(user.db_config)
db = Session()
accounts = db.query(Account).all()
transactions = db.query(Transaction).all()
entries = db.query(BookEntry).all()
tree = AccountsTree.from_db()
