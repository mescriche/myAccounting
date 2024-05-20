__author__ = 'Manuel Escriche'

import os, json,locale, re
from datetime import datetime
from dbase import db_session, Transaction, Account


def db_currency(data:float) -> str:
    return locale.currency(data, symbol=False, grouping=True)

def db_get_account_code(gname:str) -> str:
    ptrn = re.compile(r'\[((C|D)(R|N))-(?P<code>\d+)\]\s[-\/\s\w]+')
    if match := ptrn.fullmatch(gname):
        code = match.group('code')
        return code
    else:
        raise Exception(f'Wrong account pattern:"{gname}"')

def db_get_accounts_gname(all=True) -> list:
    with db_session() as db:
        accounts = db.query(Account).all() if all else filter(lambda x: not x.isEmpty, db.query(Account).all())
        acc_gnames = [account.gname for account in sorted(accounts, key=lambda x:x.code)]
    return acc_gnames
    
def db_get_yearRange() -> tuple:
    today = datetime.today()
    with db_session() as db:
        if first := db.query(Transaction).order_by(Transaction.date.asc()).first():
            _min = first.date.year
        else: _min = today.year
        if last := db.query(Transaction).order_by(Transaction.date.desc()).first():
            _max = last.date.year
        else: _max = today.year
    return _min,_max
