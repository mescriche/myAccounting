from tkinter import *
from tkinter import ttk
from dbase import db_session, db_currency, Account
from locale import currency

class LedgerView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.pack(fill='both', expand=True)
        self.text = Text(self)
        self.text.pack(fill='both', expand=True)
        self.text.tag_configure('account', background='blue')
        self.render()

    def render(self):
        self.text['state'] = 'normal'
        self.text.delete('1.0', 'end')
        with db_session() as db:
            for account in db.query(Account).all():
                if not account.debit and not account.credit: continue 
                self.text.insert('end', f"{account.gname:<112}", ('account'))
                self.text.insert('end', '\n')
                self.text.insert('end', f"{'':-^112}\n")
                self.text.insert('end', f"| {'EId':>4} | {'TId':>4} | {'Date':^10} | {'Debit':^10} | {'Credit':^10} | {'Description':<55} |\n")
                self.text.insert('end', f"{'':-^112} \n")
                for entry in account.entries:
                    line = f"| {entry.id:>4} | {entry.transaction.id:>4} | {entry.transaction.date} | {db_currency(entry.debit):>10} | {db_currency(entry.credit):>10} | {entry.transaction.description:<55} |\n"
                    self.text.insert('end', line)
                self.text.insert('end', f"{'':-^112}\n")
                self.text.insert('end', '\n')
        self.text['state'] = 'disabled'
                                   
