from enum import Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, ForeignKey, Integer, String, Date, DateTime, Float, PickleType
from sqlalchemy.orm import relationship, backref, object_session
from sqlalchemy import func, select, CheckConstraint
from datetime import datetime, date

Base = declarative_base()

class Account(Base):
    __tablename__ = 'accounts'
    id = Column(Integer, primary_key=True)
    type = Column(String(6))
    code = Column(String(6),  unique=True)
    name = Column(String(50), unique=True)
    entries = relationship('BookEntry', back_populates='account')

    __mapper_args__ = {
        'polymorphic_on': type,
        'polymorphic_identity': 'account'
    }

    @property
    def debit(self) -> float:
        return sum((entry.debit for entry in self.entries))
    
    @property
    def credit(self) -> float:
        return sum((entry.credit for entry in self.entries))

    def __repr__(self):
        return "Account({0.id} | {0.type} | {0.name})".format(self)

class Asset(Account):
    __mapper_args__ = {
        'polymorphic_identity': 'asset'
    }
    
    @property
    def gname(self) -> str:
        return '[{}][D] {}'.format(self.code, self.name)
    
    @property
    def balance(self) -> float:
        return self.debit - self.credit
    
class Claim(Account):
    __mapper_args__ = {
        'polymorphic_identity': 'claim'
    }
    
    @property
    def gname(self) -> str:
        return '[{}][C] {}'.format(self.code, self.name)
    
    @property
    def balance(self) -> float:
        return self.credit - self.debit
    
class BookEntry(Base):
    __tablename__ = 'ledger'
    id = Column(Integer, primary_key=True)
    account_id = Column(Integer, ForeignKey('accounts.id'), nullable=False)
    account = relationship('Account', back_populates='entries')
    transaction_id = Column(Integer, ForeignKey('journal.id'))
    transaction = relationship('Transaction', back_populates='entries')
    debit = Column(Float, nullable=False, default=0) # debit and credit fields joined
    credit = Column(Float, nullable=False, default=0)
    __table_args__ = (
        CheckConstraint('debit  >= 0.0'),
        CheckConstraint('credit >= 0.0')
    )

    def __repr__(self):
        return "Entry({0.id} | {0.account.name} | {0.transaction_id} | {0.amount} | {0.balance})".format(self)

    
class Transaction(Base):
    __tablename__ = 'journal'
    id = Column(Integer, primary_key=True)
    date = Column(Date)
    description = Column(String)
    entries = relationship('BookEntry', back_populates='transaction')
    
    @property
    def debit(self) -> float:
        return sum((entry.debit for entry in self.entries))

    @property
    def credit(self) -> float:
        return sum((entry.credit for entry in self.entries))

    def __repr__(self):
        return "Transaction({0.id} | {0.date}} | #entries={1} | {0.description})".format(self, len(self.entries))
