__author__ = 'Manuel Escriche'
from tkinter import *
from tkinter import ttk

from dbase import db_session, db_get_yearRange, db_currency
from dbase import Account, Content, Type #, db_get_year


class MapView(ttk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.pack(fill='both', expand=True)

        columns = 'account', 'debit', 'credit', 'debtor', 'creditor'
        data = dict()
        data['account'] = {'text':'Account' , 'width':120, 'anchor':'w'}
        data['debit'] =   {'text':'Debit', 'width':80, 'anchor':'e'}
        data['credit'] =  {'text':'Credit', 'width':80, 'anchor':'e'}
        data['debtor'] =  {'text':'Debtor', 'width':80, 'anchor':'e'}
        data['creditor'] = {'text':'Creditor', 'width':80, 'anchor':'e'}

        self.table = ttk.Treeview(self, columns=columns, selectmode='browse', show='headings')
        self.table.pack(fill='both', expand=True)
        for topic in columns:
            self.table.heading(topic, text=data[topic]['text'])
            self.table.column(topic, width=data[topic]['width'], anchor=data[topic]['anchor'])
        self.table.tag_configure('even', background='gray90')
        self.table.tag_configure('total', background='SteelBlue1')
        self.table.tag_configure('error', background='salmon')
        self.table.bind("<<TreeviewSelect>>", self.display_account)
        
            
        year_min, year = db_get_yearRange()
        total = {'debit':0, 'credit':0, 'debtor':0, 'creditor':0}
        with db_session() as db:
            for account in db.query(Account).filter_by(content=Content.REAL).filter_by(type=Type.CREDIT):
                debit = account.debit(year)
                credit = account.credit(year)
                balance = account.balance(year)
                values = account.gname, db_currency(debit), db_currency(credit),\
                    db_currency(balance) if balance < 0 else '-' ,\
                    db_currency(balance) if balance > 0 else '-'
                if balance != 0:
                    self.table.insert('','end', values=values )
                total['debit']+= debit
                total['credit'] += credit
                total['creditor'] += balance if balance > 0 else 0
                total['debtor'] += balance if balance < 0 else 0
            for account in db.query(Account).filter_by(content=Content.REAL).filter_by(type=Type.DEBIT):
                debit = account.debit(year)
                credit = account.credit(year)
                balance = account.balance(year)
                values = account.gname, db_currency(debit), db_currency(credit),\
                    db_currency(balance) if balance > 0 else '-' ,\
                    db_currency(balance) if balance < 0 else '-'
                if balance != 0:
                    self.table.insert('','end', values=values )
                total['debit']+= debit
                total['credit'] += credit
                total['creditor'] += balance if balance < 0 else 0
                total['debtor'] += balance if balance > 0 else 0
            for account in db.query(Account).filter_by(content=Content.NOMINAL).filter_by(type=Type.CREDIT):
                debit = account.debit(year)
                credit = account.credit(year)
                balance = account.balance(year)
                values = account.gname, db_currency(debit), db_currency(credit),\
                    db_currency(balance) if balance < 0 else '-' ,\
                    db_currency(balance) if balance > 0 else '-'
                if balance != 0:
                    self.table.insert('','end', values=values )
                total['debit']+= debit
                total['credit'] += credit
                total['creditor'] += balance if balance > 0 else 0
                total['debtor'] += balance if balance < 0 else 0
            for account in db.query(Account).filter_by(content=Content.NOMINAL).filter_by(type=Type.DEBIT):
                debit = account.debit(year)
                credit = account.credit(year)
                balance = account.balance(year)
                values = account.gname, db_currency(debit), db_currency(credit),\
                    db_currency(balance) if balance > 0 else '-' ,\
                    db_currency(balance) if balance < 0 else '-'
                if balance != 0:
                    self.table.insert('','end', values=values )
                total['debit']+= debit
                total['credit'] += credit
                total['creditor'] += balance if balance > 0 else 0
                total['debtor'] += balance if balance < 0 else 0
        values = 'TOTAL', db_currency(total['debit']), db_currency(total['credit']),\
            db_currency(total['debtor']), db_currency(total['creditor'])
        total_iid = self.table.insert('','end', values=values, tag='total')
        
        if total['debit'] != total['credit']: self.table.item(total_iid, tag='error')
        if total['debtor'] != total['creditor']: self.table.item(total_iid, tag='error')
        
        for n,iid in enumerate(self.table.get_children()):
            if iid == total_iid: continue
            if n%2 == 0: self.table.item(iid, tag='even')
        
    def display_account(self, event):
        if iid := event.widget.focus():
            account_gname = event.widget.set(iid, column='account')
            self.master.master.ledger.account.set(account_gname)
            self.master.master.ledger.render_filter()
            self.master.master.notebook.select(2)
        return 'break'

