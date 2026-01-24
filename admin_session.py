import os
from datamodel import UserData, AccountsTree
from dbase import db_open, Session, Account, Seat, BookEntry
from sqlalchemy import select

root = os.getcwd()
user =  db = accounts = seats = entries = tree = None

def init(_user_ = 'mev'):
    global user, db, accounts, seats, entries, tree
    user = UserData(root, _user_)
    db_open(user.db_config)
    db = Session()
    accounts = db.query(Account).all()
    seats = db.query(Seat).all()
    entries = db.query(BookEntry).all()
    tree = AccountsTree.from_db()

def list_accounts():
    for entry in accounts: print(entry)

def get_account(code):
    return next(filter(lambda x: x.code == str(code), accounts))

def show_entries_in_account(code, n_items='all'):
    n_items = 0 if n_items == 'all' else n_items
    acc = next(filter(lambda x: x.code == str(code), accounts))
    print(acc)
    if len(acc.entries) > 0:
        _n_items = 0
        for entry in acc.entries:
            print(entry.seat.date, entry, entry.seat.description)
            _n_items += 1
            if n_items == _n_items: break
    else:
        print("Empty account")

def list_seats():
    for seat in seats: print(seat)
        
def search_seats_by_description(desc):
    for seat in seats:
        if desc in seat.description:
            print(seat)
    
def get_entry(id, prnt=False):
    entry = next(filter(lambda x:x.id ==id, entries))
    if prnt:
        print(entry)
        print(entry.seat)
    return entry

def get_seat(id, prnt=False):
    seat = next(filter(lambda x:x.id == id, seats))
    if prnt:
        print(seat)
        for entry in seat.entries:
            print(entry)
    return seat        

def move_entry_to_account(entry_id, code):
    acc = find_account(code)
    entry = next(filter(lambda x:x.id == entry_id, entries), None)
    _from = entry.account.code
    entry.account_id = acc.id
    db.commit()
    print(f"From account {_from} to {entry.account.code}: {entry}")    

def move_entries_to_account(ids:list, code):
    acc = find_account(code)
    for _id in ids:
        entry = next(filter(lambda x:x.id == _id, entries), None)
        _from = entry.account.code
        entry.account_id = acc.id
        print(f"From account {_from} to {acc.code}: {entry}")
    else:
        db.commit()
    
def search_seats_by_id(id):
    seat = next(filter(lambda x:x.id == id, seats))
    print(seat)
    return seat
