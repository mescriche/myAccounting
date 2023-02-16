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
    assets_file = 'assets.json'
    DIR = path.dirname(path.realpath(__file__))
    data = dict()
    with open(path.join(DIR, assets_file)) as afile,  db_session() as db:
        assets = load(afile)
        for record in assets:
            try: asset = db.query(Asset).filter_by(name=record['name']).one()
            except NoResultFound:
                db.add(Asset(**record))
                
    claims_file = 'claims.json'    
    with open(path.join(DIR, claims_file)) as cfile, db_session() as db:
        claims = load(cfile)
        for record in claims:
            try: claim = db.query(Claim).filter_by(name=record['name']).one()
            except NoResultFound:
                db.add(Claim(**record))
        
db_setup()


