from tkinter import *
from tkinter import ttk
from dbase import db_session, db_currency, Account
from locale import currency

class LedgerView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        pw = ttk.Panedwindow(self, orient=VERTICAL)
        pw.pack(fill='both', expand=True)

        acc_pw = ttk.Panedwindow(pw, orient=HORIZONTAL)
        pw.add(acc_pw, weight=1)

        debit_acc_frame = ttk.Labelframe(acc_pw, text='Assets', labelanchor='n')
        acc_pw.add(debit_acc_frame, weight=1)
        columns = ('id', 'name', '#entries', 'balance')
        self.debit_accounts = ttk.Treeview(debit_acc_frame, columns=columns, show='headings')
        self.debit_accounts.pack(fill='both', expand=True)
        self.debit_accounts.heading('id', text='Id')
        self.debit_accounts.column('id', width=25, stretch=False, anchor='c')
        self.debit_accounts.heading('name', text='Name')
        self.debit_accounts.column('name', width=150, anchor='w')
        self.debit_accounts.heading('#entries', text='#entries')
        self.debit_accounts.column('#entries', width=25,  anchor='c')
        self.debit_accounts.heading('balance', text='Balance')
        self.debit_accounts.column('balance', width=75,  anchor='e')
        self.debit_accounts.tag_configure('total', background='#cccccc')
        self.debit_accounts.bind('<<TreeviewSelect>>', self.render_debit_entries)

        
        credit_acc_frame = ttk.Labelframe(acc_pw, text='Claims', labelanchor='n')
        acc_pw.add(credit_acc_frame, weight=1)
        columns = ('id', 'name', '#entries', 'balance')
        self.credit_accounts = ttk.Treeview(credit_acc_frame, columns=columns, show='headings')
        self.credit_accounts.pack(fill='both', expand=True)
        self.credit_accounts.heading('id', text='Id')
        self.credit_accounts.column('id', width=25, stretch=False, anchor='c')
        self.credit_accounts.heading('name', text='Name')
        self.credit_accounts.column('name', width=150, anchor='w')
        self.credit_accounts.heading('#entries', text='#entries')
        self.credit_accounts.column('#entries', width=25,  anchor='c')
        self.credit_accounts.heading('balance', text='Balance')
        self.credit_accounts.column('balance', width=75,  anchor='e')
        self.credit_accounts.bind('<<TreeviewSelect>>', self.render_credit_entries)
        self.credit_accounts.tag_configure('total', background='#cccccc')
        self.render_accounts()

        
        entries_frame = ttk.Frame(pw) 
        pw.add(entries_frame, weight=1)
        columns = ('id', 'trans','date', 'description', 'debit', 'credit')
        self.entries = ttk.Treeview(entries_frame, columns=columns, show='headings')
        self.entries.pack(fill='both', expand=True)
        self.entries.heading('id', text='Id')
        self.entries.column('id', width=25, stretch=False, anchor='c')
        self.entries.heading('trans', text='TrId')
        self.entries.column('trans', width=50, stretch=False, anchor='c')
        self.entries.heading('date', text='Date')
        self.entries.column('date', width=100, stretch=False, anchor='c')
        self.entries.heading('description', text='Description')
        self.entries.column('description',  anchor='w')
        self.entries.heading('debit', text='Debit')
        self.entries.column('debit', width=75, stretch=False, anchor='e')
        self.entries.heading('credit', text='Credit')
        self.entries.column('credit', width=75, stretch=False, anchor='e')
        self.entries.tag_configure('total', background='#cccccc')

    def render_accounts(self, *args):
        self.debit_accounts.delete(*self.debit_accounts.get_children())
        self.credit_accounts.delete(*self.credit_accounts.get_children())
        assets_balance, claims_balance = 0,0
        with db_session() as db:
            for acc in db.query(Account).all():
                if acc.type == 'asset': assets_balance += acc.balance
                if acc.type == 'claim': claims_balance += acc.balance
            
        if assets_balance != claims_balance: raise Exception("BalanceError")
        assets_balance_currency = currency(assets_balance, symbol=False, grouping=True) 
        claims_balance_currency = currency(claims_balance, symbol=False, grouping=True)
        
        self.debit_accounts.insert('', 'end', values=('','','', assets_balance_currency), tag='total')
        self.credit_accounts.insert('','end', values=('','','', claims_balance_currency), tag='total')
        
        with db_session() as db:
            for acc in db.query(Account).all():
                if acc.type == 'asset':
                    balance = currency(acc.balance, symbol=False, grouping=True)
                    self.debit_accounts.insert('','end', text=acc.name,
                                               values=(acc.id, acc.gname, len(acc.entries), balance))
                if acc.type == 'claim':
                    balance = currency(acc.balance, symbol=False, grouping=True)
                    self.credit_accounts.insert('', 'end', text=acc.name,
                                                values=(acc.id, acc.gname, len(acc.entries),balance))
                    
    def render_debit_entries(self, *args):
        self.entries.delete(*self.entries.get_children())
        item_id = self.debit_accounts.focus()
        account_name = self.debit_accounts.item(item_id)['text']
        with db_session() as db:
            try:
                account = db.query(Account).filter_by(name=account_name).one()
            except: pass
            else:
                self.entries.insert('','end', values=('','','','', db_currency(account.debit),
                                                      db_currency(account.credit)), tag='total')
                for entry in reversed(account.entries):
                    self.entries.insert('','end', values=(entry.id, entry.transaction.id,
                                                          entry.transaction.date, entry.transaction.description,
                                                          db_currency(entry.debit), db_currency(entry.credit)))
                
    def render_credit_entries(self, *args):
        self.entries.delete(*self.entries.get_children())
        item_id = self.credit_accounts.focus()
        account_name = self.credit_accounts.item(item_id)['text']
        with db_session() as db:
            try:
                account = db.query(Account).filter_by(name=account_name).one()
            except: pass
            else:
                self.entries.insert('','end',
                                    values=('','','','', db_currency(account.debit),
                                            db_currency(account.credit)),tag='total')
                for entry in reversed(account.entries):
                    self.entries.insert('','end',
                                        values=(entry.id, entry.transaction.id,
                                                entry.transaction.date, entry.transaction.description,
                                                db_currency(entry.debit), db_currency(entry.credit))) 

    def render(self):
        self.render_accounts()
        self.render_debit_entries()
        self.render_credit_entries()
