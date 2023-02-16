from enum import Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.orderinglist import ordering_list
from sqlalchemy import Column, ForeignKey, Integer, String, Date, DateTime, Float, PickleType
from sqlalchemy.orm import relationship, backref, object_session
from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy.ext.hybrid import Comparator, hybrid_property, hybrid_method
from sqlalchemy import func, select
from datetime import datetime, date

Base = declarative_base()

class Account(Base):
    __tablename__ = 'accounts'
    id = Column(Integer, primary_key=True)
    type = Column(String(6))
    name = Column(String(50))
    entries = relationship('BookEntry', back_populates='account')

    __mapper_args__ = {
        'polymorphic_on': type,
        'polymorphic_identity': 'account'
    }

    @property
    def balance(self) -> float:
        try:
            _balance =  self.entries[-1].balance
        except IndexError:
            _balance =  0.0
        finally:
            return _balance
        
    def __repr__(self):
        return "Account({0.id} | {0.type} | {0.name})".format(self)

class Asset(Account):
    __mapper_args__ = {
        'polymorphic_identity': 'asset'
    }

    
class Claim(Account):
    __mapper_args__ = {
        'polymorphic_identity': 'claim'
    }

    
class BookEntry(Base):
    __tablename__ = 'ledger'
    id = Column(Integer, primary_key=True)
    account_id = Column(Integer, ForeignKey('accounts.id'), nullable=False)
    account = relationship('Account', back_populates='entries')
    transaction_id = Column(Integer, ForeignKey('journal.id'))
    transaction = relationship('Transaction', back_populates='entries')
    amount = Column(Float) # debit and credit fields joined
    balance = Column(Float)

    def __init__(self, account, transaction, amount, balance):
        self.account = account
        self.transaction = transaction
        self.amount = amount
        self.balance = balance + amount
        
    def __repr__(self):
        return "Entry({0.id} | {0.account.name} | {0.transaction_id} | {0.amount} | {0.balance})".format(self)

    
class Transaction(Base):
    __tablename__ = 'journal'
    id = Column(Integer, primary_key=True)
    date = Column(Date)
    description = Column(String)
    entries = relationship('BookEntry', back_populates='transaction')   
    
    def __repr__(self):
        return "Transaction({0.id} | {0.date}} | #entries={1} | {0.description})".format(self, len(self.entries))
