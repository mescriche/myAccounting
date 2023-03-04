from tkinter import *
from tkinter import ttk
from dbase import db_session, db_currency, Account
from locale import currency

class LedgerView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.pack(fill='both', expand=True)
        self.ledger = Text(self)
        self.ledger.pack(fill='both', expand=True)
        self.ledger.tag_configure('account', background='blue')
        self.render()

    def render(self):
        self.ledger['state'] = 'normal'
        self.ledger.delete('1.0', 'end')
        with db_session() as db:
            for account in db.query(Account).all():
                if not account.debit and not account.credit: continue 
                self.ledger.insert('end', '{}\n'.format(account.gname), ('account'))
                self.ledger.insert('end', '{:-^112} \n'.format('-'))
                self.ledger.insert('end', '| {:>4} | {:>4} | {:^10} | {:^10} | {:^10} | {:<55} |\n'.format('EId', 'TId', 'Date', 'Debit', 'Credit', 'Description'))
                self.ledger.insert('end', '{:-^112} \n'.format('-'))
                for entry in account.entries:
                    self.ledger.insert('end', '| {:>4} | {:>4} | {} | {:>10} | {:>10} | {:<55} |\n'.format(entry.id, entry.transaction.id, entry.transaction.date,  db_currency(entry.debit), db_currency(entry.credit), entry.transaction.description))
                self.ledger.insert('end', '{:-^112} \n\n'.format('-'))      
        self.ledger['state'] = 'disabled'
                                   
