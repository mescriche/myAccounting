__author__ = 'Manuel Escriche'

import os, json
from contextlib import contextmanager
from sqlalchemy import engine_from_config
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound
from .model import Base, Account, Transaction, BookEntry, Type, Content


Session = sessionmaker()


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


def db_init(config):
    engine = engine_from_config(config)
    Base.metadata.create_all(bind=engine)
    Session.configure(bind=engine)

def db_open(config):
    engine = engine_from_config(config)
    Session.configure(bind=engine)    
            
def db_setup(accounts_file):
    with open(accounts_file) as acc_file, db_session() as db:
        data = json.load(acc_file)
        for record in data:
            try: account = db.query(Account).filter_by(code=record['code']).one()
            except NoResultFound:
                db.add(Account(**record))
                print("Created account: type:{type} content:{content} code:{code} name:{name}".format(**record))
