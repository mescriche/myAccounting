from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, ForeignKey, Integer, String, Date, DateTime, Float, PickleType
from sqlalchemy.orm import relationship, backref, object_session
from sqlalchemy import func, select, CheckConstraint
from datetime import datetime, date
from sqlalchemy import Enum
import enum

Base = declarative_base()

Type = enum.Enum('Type', ['DEBIT', 'CREDIT'])
Content = enum.Enum('Content', ['REAL', 'NOMINAL']) 
#Content = enum.Enum('Content', ['STATE', 'FLOW'])
#Content = enum.Enum('Content', ['PROPERTY', 'ACTIVITY'])
#Content = enum.Enum('Content', ['BALANCE', 'INCOME'])

class Account(Base):
    __tablename__ = 'accounts'
    id = Column(Integer, primary_key=True)
    type = Column(Enum(Type))
    content = Column(Enum(Content))
    code = Column(String(6),  unique=True)
    name = Column(String(50), unique=True)
#    attributes = Column(PickleType)
    entries = relationship('BookEntry', back_populates='account')

    @property
    def debit(self) -> float:
        return sum((entry.debit for entry in self.entries))
    
    @property
    def credit(self) -> float:
        return sum((entry.credit for entry in self.entries))
    
    @property
    def isEmpty(self) -> bool:
        try: item = entries[0]
        except IndexError: return True
        else: return False
        
    @property
    def isReal(self) -> bool:
        return True if self.content == Content.REAL else False

    @property
    def isNominal(self) -> bool:
        return True if self.content == Content.NOMINAL else False

    @property
    def isAsset(self) -> bool:
        return True if self.type == Type.DEBIT and self.content == Content.REAL  else False

    @property
    def isClaim(self) -> bool:
        return True if self.type == Type.CREDIT and self.content == Content.REAL else False

    def __repr__(self):
        return "Account({0.id} | {0.type} | {0.content} | {0.code} | {0.name} )".format(self)

    @property
    def gname(self) -> str:
        if self.type == Type.DEBIT:
            if self.content == Content.REAL:
                return '[DR-{}] {}'.format(self.code, self.name)
            elif self.content == Content.NOMINAL:
                return '[DN-{}] {}'.format(self.code, self.name)
            else: raise Exception('Unknown Account content')
        elif self.type == Type.CREDIT:
            if self.content == Content.REAL:
                return '[CR-{}] {}'.format(self.code, self.name)
            elif self.content == Content.NOMINAL:
                return '[CN-{}] {}'.format(self.code, self.name)
            else: raise Exception('Unknown Account content')
        else: raise Exception('Unknown Account type')
        
    @property
    def balance(self) -> float:
        if self.type == Type.DEBIT:
            return self.debit - self.credit
        elif self.type == Type.CREDIT:
            return self.credit - self.debit
        else: raise Exception('Unknown Account type')
    
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
        return "Transaction({0.id} | {0.date} | #entries={1} | {0.description})".format(self, len(self.entries))
