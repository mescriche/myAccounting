__author__ = 'Manuel Escriche'
from os import path
from json import load
from datetime import datetime
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound
from .model import Base, Account, Transaction, BookEntry
from collections import namedtuple
import locale, re

def db_get_profile() -> str:
    accounts_file = 'accounts.json'
    DIR = path.dirname(path.realpath(__file__))
    with open(path.join(DIR, accounts_file)) as _file:
        config_data = load(_file)
    return config_data['profile']

def db_init():
    dbfile = 'accounting.db'
    DIR = path.dirname(path.realpath(__file__))
    engine = create_engine ('sqlite+pysqlite:///{}'.format(path.join(DIR, dbfile)))
    Base.metadata.bind = engine
    Base.metadata.create_all(bind=engine)
    return sessionmaker(bind=engine)

Session = db_init()

@contextmanager
def db_session():
    session = Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()

def db_currency(data:float) -> str:
    return locale.currency(data, symbol=False, grouping=True)
    
        
def db_setup():
    DIR = path.dirname(path.realpath(__file__))
    accounts_file = 'accounts.json'    
    with open(path.join(DIR, accounts_file)) as acc_file, db_session() as db:
        data = load(acc_file)
        if 'purpose' not in data: raise Exception('Wrong data file format')
        elif data['purpose'] != 'database': raise Exception('Wrong purpose for accounts definition')
        else: pass
        if 'accounts' not in data: raise Exception('Missing accounts field')
        elif not isinstance(data['accounts'], list): Exception('Wrong format in list of accounts')
        else:
            for record in data['accounts']:
                try: account = db.query(Account).filter_by(name=record['name']).one()
                except NoResultFound:
                    db.add(Account(**record))
                    print("Created account: type:{type} content:{content} code:{code} name:{name}".format(**record))
                #else:
                    #print("{} already existing in data base".format(account))
db_setup()


def db_get_account_code(gname:str) -> str:
    ptrn = re.compile(r'\[((C|D)(R|N))-(?P<code>\d+)\]\s[-\/\s\w]+')
    if match := ptrn.fullmatch(gname):
        code = match.group('code')
        return code
    else:
        raise Exception(f'Wrong account pattern:"{gname}"')

def db_get_accounts_gname() -> list:
    with db_session() as db:
        accounts = filter(lambda x: not x.isEmpty, db.query(Account).all())
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
