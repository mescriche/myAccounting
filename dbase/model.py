__author__ = 'Manuel Escriche'
from sqlalchemy import Enum, Integer, String, Date, DateTime, Float, JSON 
from sqlalchemy.orm import relationship, object_session
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, validates
from sqlalchemy import func, select, ForeignKey, CheckConstraint
#from datetime import datetime, date
import enum, re, json, datetime

#Base = declarative_base()
class Base(DeclarativeBase):
    pass

Type = enum.Enum('Type', ['DEBIT', 'CREDIT'])
Content = enum.Enum('Content', ['REAL', 'NOMINAL']) 
#Content = enum.Enum('Content', ['STATE', 'FLOW'])
#Content = enum.Enum('Content', ['BALANCE', 'INCOME'])

class Account(Base):
    __tablename__ = 'book'
    id: Mapped[int] = mapped_column(primary_key=True)
    type: Mapped[Type] = mapped_column()
    content: Mapped[Content] = mapped_column()
    code: Mapped[str] = mapped_column(String(6),  unique=True)
    path: Mapped[str] = mapped_column(String(50), nullable=True)
    name: Mapped[str] = mapped_column(String(20), unique=True)
    parameters: Mapped[dict] = mapped_column(JSON, nullable=True)
    entries: Mapped[list['BookEntry']] = relationship(back_populates='account')  # many-to-one

    def debit(self, year=None) -> float:
        entries = filter(lambda x:x.transaction.date.year == year, self.entries) if year else self.entries
        return sum((entry.debit for entry in entries))
    
    def credit(self, year=None) -> float:
        entries = filter(lambda x:x.transaction.date.year == year, self.entries) if year else self.entries
        return sum((entry.credit for entry in entries))
    
    @property
    def isEmpty(self) -> bool:
        try: item = self.entries[0]
        except IndexError: return True
        else: return False

    def isQuiet(self, year=None) -> bool:
        entries = filter(lambda x:x.transaction.date.year == year, self.entries) if year else self.entries
        try: next(entries)
        except StopIteration: return True
        else: return False
        
    @property
    def isReal(self) -> bool:
        return True if self.content == Content.REAL else False

    @property
    def isNominal(self) -> bool:
        return True if self.content == Content.NOMINAL else False

    @property
    def isAsset(self) -> bool:
        return True if self.type == Type.DEBIT and\
            self.content == Content.REAL  else False

    @property
    def isClaim(self) -> bool:
        return True if self.type == Type.CREDIT and\
            self.content == Content.REAL else False
    
    @property
    def isInput(self) -> bool:
        return True if self.type == Type.CREDIT and\
            self.content == Content.NOMINAL else  False

    @property
    def isOutput(self) ->bool:
        return True if self.type == Type.DEBIT and\
            self.content == Content.NOMINAL else False
    

    def __repr__(self):
        return "Account({0.id} | {0.type} | {0.content} | {0.code} | {0.path} |{0.name} | {0.parameters} )".format(self)

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
        
        
    def balance(self, year=None) -> float:
        if year:
            if self.type == Type.DEBIT:
                return self.debit(year) - self.credit(year)
            elif self.type == Type.CREDIT:
                return self.credit(year) - self.debit(year)
            else: raise Exception('Unknown Account type')
        else:
            if self.type == Type.DEBIT:
                return self.debit() - self.credit()
            elif self.type == Type.CREDIT:
                return self.credit() - self.debit()
            else: raise Exception('Unknown Account type')

    @property
    def lname(self)->str:
        return self.path + '/'+ self.name
    
    @validates('path')
    def validate_path(self, key, value):
        #return value
        #setattr(self, key, value)
        if self.isAsset and 'assets' not in value or \
           self.isClaim and 'claims' not in value or \
           self.isInput and 'input' not in value or \
           self.isOutput and 'output' not in value:
            raise ValueError('Inconsistent account declaration with code hierarchy')
        else:
            return value
    
    
class BookEntry(Base):
    __tablename__ = 'ledger'
    id: Mapped[int] = mapped_column(primary_key=True)
    account_id: Mapped[int] = mapped_column(ForeignKey('book.id'), nullable=False)
    account: Mapped['Account'] = relationship(back_populates='entries')
    transaction_id: Mapped[int] = mapped_column(ForeignKey('journal.id'))
    transaction: Mapped['Transaction'] = relationship( back_populates='entries')
    type: Mapped[Type]  = mapped_column()
    amount: Mapped[float] = mapped_column(Float, CheckConstraint('amount >= 0.0'), default=0)
        
    @property
    def value(self) -> float:
        return self.amount if self.account.type == self.type else -self.amount

    @property
    def credit(self) -> float:
        return self.amount if self.type == Type.CREDIT else 0.0

    @property
    def debit(self) -> float:
        return self.amount if self.type == Type.DEBIT else 0.0
        
    def __repr__(self):
        return "Entry({0.id} | {0.account.name} | {0.transaction_id} | {0.type} | {0.amount} )".format(self)

    
class Transaction(Base):
    __tablename__ = 'journal'
    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    description: Mapped[str] = mapped_column(String)
    entries: Mapped[list['BookEntry']] = relationship(back_populates='transaction')
    
    @property
    def debit(self) -> float:
        return sum((entry.debit for entry in self.entries))

    @property
    def credit(self) -> float:
        return sum((entry.credit for entry in self.entries))

    def __repr__(self):
        return "Transaction({0.id} | {0.date} | #entries={1} | {0.description})".format(self, len(self.entries))
