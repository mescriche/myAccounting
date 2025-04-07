__author__ = 'Manuel Escriche'

import os, json
from contextlib import contextmanager
from sqlalchemy import engine_from_config
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound
from .model import Base, Account, Transaction, BookEntry, Type, Content
from .paths import find_path

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
            
def db_setup(accounts_file, verbose=False):
    with open(accounts_file) as acc_file,  db_session() as db:
        data = json.load(acc_file)
        for n,record in enumerate(data,start=1):
            try:
                account = db.query(Account).filter_by(code=record['code']).one()
            except NoResultFound:
                record['path'] =  find_path(record['code'])
                db.add(Account(**record))
                if verbose:
                    print(f"{n} ... created account: type:{record['type']} content:{record['content']} code:{record['code']} name:{record['name']} path:{record['path']}")
            else:
                record['path'] =  find_path(record['code'])
                if 'parameters' not in record: record['parameters'] = None
                v0 = ('type', 'content', 'path', 'name', 'parameters')
                v1 = (account.type.name, account.content.name, account.path, account.name, account.parameters)
                v2 = (record['type'], record['content'], record['path'], record['name'],record['parameters'])
                if any(a != b for a,b in zip(v1, v2)):
                    if account.type.name != record['type']:
                        account.type = record['type']
                        if verbose:
                            print(f"{n} ... updated type in {account}")
                    if account.content.name != record['content']:
                        account.content = record['content']
                        if verbose:
                            print(f"{n} ... updated content in {account}")
                    if account.path != record['path']:
                        account.path = record['path']
                        if verbose:
                            print(f"{n} ... updated path in {account}")
                    if account.name != record['name']:
                        account.name = record['name']
                        if verbose:
                            print(f"{n} ... updated name in {account}")
                    if account.parameters != record['parameters']:
                        account.parameters = record['parameters']
                        if verbose:
                            print(f"{n} ... updated parameters in {account}")
                
