from os import path
from json import load
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound
from .model import Base, Account, Asset, Claim, Transaction, BookEntry
from collections import namedtuple


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
       
def db_setup():
    DIR = path.dirname(path.realpath(__file__))
    accounts_file = 'accounts.json'    
    with open(path.join(DIR, accounts_file)) as acc_file, db_session() as db:
        accounts = load(acc_file)
        for record in accounts:
            try: account = db.query(Account).filter_by(name=record['name']).one()
            except NoResultFound:
                db.add(Account(**record))
                print("Created account: {}".format(account.gname))
            else: pass
db_setup()


