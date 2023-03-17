from tkinter import *
from tkinter import ttk
from dbase import db_session, db_currency, Transaction

class JournalView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.pack(fill='both', expand=True)
        self.text = Text(self)
        self.text.pack(fill='both', expand=True)
        self.text.tag_configure('transaction', foreground='yellow', justify='left')
        self.text.tag_configure('account', background='blue')
        #self.journal.tag_bind('account', "<Button-1>" , self.account_in_ledger)
        self.render()
        
    def account_in_ledger(self, event):
        print('account_in_ledger')
        index = self.journal.index('@{},{}'.format(event.x, event.y))
        tag_indices = list(self.journal.tag_ranges('account'))
        for start, end in zip(*[iter(tag_indices)]*2):
            if self.journal.compare(start, '<=', index) and self.journal.compare(index, '<', end):
                account = self.journal.get(start, end)
                self.parent.select(1)
                break
        else:
            print('Account not found')
        
    def render(self):
        self.text['state'] = 'normal'
        self.text.delete('1.0', 'end')
        with db_session() as db:
            for trans in reversed(db.query(Transaction).all()):
                self.text.insert('end', '{:=^60} \n'.format(' Transaction #{} '.format(trans.id)), ('transaction'))
                self.text.insert('end', 'Date: {:%d-%m-%Y} \n'.format(trans.date))
                self.text.insert('end', 'Description: {} \n'.format(trans.description))
                self.text.insert('end', '{:-^60} \n'.format('-'))
                self.text.insert('end', '| {:^10} | {:^30} | {:^10} |\n'.format('Debit', 'Account', 'Credit'))
                self.text.insert('end', '{:-^60} \n'.format('-'))
                for entry in trans.entries:
                    #values = (db_currency(entry.debit), entry.account.gname, db_currency(entry.credit))
                    #self.text.insert('end', '| {:>10} | {:<30} | {:>10} |\n'.format(*values), ('account'))
                    self.text.insert('end', '| {:>10} |'.format(db_currency(entry.debit)))
                    self.text.insert('end', ' {:<30} '.format(entry.account.gname), ('account'))
                    self.text.insert('end', '| {:>10} |\n'.format(db_currency(entry.credit)))
                self.text.insert('end', '{:-^60} \n'.format('-'))
                values = (db_currency(trans.debit), '', db_currency(trans.credit))
                self.text.insert('end', '| {:>10} | {:<30} | {:>10} |\n'.format(*values))
        self.text['state'] = 'disabled'
        
