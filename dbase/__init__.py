from os import path
from json import load
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound
from .model import Base, Account, Transaction, BookEntry
from collections import namedtuple
import locale


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
    return locale.currency(data, symbol=False, grouping=True) if data > 0 else '-'
    
        
def db_setup():
    DIR = path.dirname(path.realpath(__file__))
    accounts_file = 'accounts.json'    
    with open(path.join(DIR, accounts_file)) as acc_file, db_session() as db:
        data = load(acc_file)
        if 'content' not in data: raise Exception('Wrong data file format')
        elif data['content'] != 'accounts': raise Exception('Wrong content for accounts definition')
        else: pass
        if 'accounts' not in data: raise Exception('Missing accounts field')
        elif not isinstance(data['accounts'], list): Exception('Wrong format in list of accounts')
        else:
            for record in data['accounts']:
                try: account = db.query(Account).filter_by(name=record['name']).one()
                except NoResultFound:
                    db.add(Account(**record))
                    print("Created account: type:{type} content:{content} code:{code} name:{name}".format(**record))
                else:
                    print("{} already existing in data base".format(account))
db_setup()


