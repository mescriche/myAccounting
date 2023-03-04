from tkinter import *
from tkinter import ttk
from dbase import db_session, db_currency, Transaction

class JournalView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.pack(fill='both', expand=True)
        self.journal = Text(self)
        self.journal.pack(fill='both', expand=True)
        self.journal.tag_configure('transaction', foreground='yellow', justify='left')
        self.journal.tag_configure('account', background='blue')
        self.render()

    def render(self):
        self.journal['state'] = 'normal'
        self.journal.delete('1.0', 'end')
        with db_session() as db:
            for trans in reversed(db.query(Transaction).all()):
                self.journal.insert('end', '{:=^60} \n'.format(' Transaction #{} '.format(trans.id)), ('transaction'))
                self.journal.insert('end', 'Date: {:%d-%m-%Y} \n'.format(trans.date))
                self.journal.insert('end', 'Description: {} \n'.format(trans.description))
                self.journal.insert('end', '{:-^60} \n'.format('-'))
                self.journal.insert('end', '| {:^10} | {:^30} | {:^10} |\n'.format('Debit', 'Account', 'Credit'))
                self.journal.insert('end', '{:-^60} \n'.format('-'))
                for entry in trans.entries:
                    #values = (db_currency(entry.debit), entry.account.gname, db_currency(entry.credit))
                    #self.text.insert('end', '| {:>10} | {:<30} | {:>10} |\n'.format(*values), ('account'))
                    self.journal.insert('end', '| {:>10} |'.format(db_currency(entry.debit)))
                    self.journal.insert('end', ' {:<30} '.format(entry.account.gname), ('account'))
                    self.journal.insert('end', '| {:>10} |\n'.format(db_currency(entry.credit)))
                self.journal.insert('end', '{:-^60} \n'.format('-'))
                values = (db_currency(trans.debit), '', db_currency(trans.credit))
                self.journal.insert('end', '| {:>10} | {:<30} | {:>10} |\n'.format(*values))
        self.journal['state'] = 'disabled'
        
