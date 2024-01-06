__author__ = 'Manuel Escriche'
from tkinter import *
from tkinter import ttk

from dbase import db_session, Account, Content, Type 
from controller.utility import db_get_yearRange, db_currency, db_get_account_code

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
        self.table.tag_configure('even_real', background='bisque')
        self.table.tag_configure('even_nominal', background='lavender')
        self.table.tag_configure('total', background='SteelBlue1')
        self.table.tag_configure('error', background='salmon')
        self.table.bind("<<TreeviewSelect>>", self.display_account)
        year_min, year = db_get_yearRange()
        self.display_data(year)
        
    def display_data(self, year):
        self.table.delete(*self.table.get_children())
        values = '-','-','-','-'
        total_iid = self.table.insert('','end', values=values, tag='total')
        with db_session() as db:
            rtotal = {'debit':0, 'credit':0, 'debtor':0, 'creditor':0}
            for account in db.query(Account).filter_by(content=Content.REAL).filter_by(type=Type.CREDIT):
                debit = account.debit(year)
                credit = account.credit(year)
                balance = account.balance(year)
                values = account.gname, db_currency(debit), db_currency(credit), '-' , db_currency(balance)
                if debit or credit:
                    self.table.insert('','end', values=values, tag='real' )
                rtotal['debit']+= debit
                rtotal['credit'] += credit
                rtotal['creditor'] += balance

            for account in db.query(Account).filter_by(content=Content.REAL).filter_by(type=Type.DEBIT):
                debit = account.debit(year)
                credit = account.credit(year)
                balance = account.balance(year)
                values = account.gname, db_currency(debit), db_currency(credit), db_currency(balance) , '-'
                if debit or credit:
                    self.table.insert('','end', values=values, tag='real' )
                rtotal['debit']+= debit
                rtotal['credit'] += credit
                rtotal['debtor'] += balance
                
            ntotal = {'debit':0, 'credit':0, 'debtor':0, 'creditor':0}
            for account in db.query(Account).filter_by(content=Content.NOMINAL).filter_by(type=Type.CREDIT):
                debit = account.debit(year)
                credit = account.credit(year)
                balance = account.balance(year)
                values = account.gname, db_currency(debit), db_currency(credit), '-', db_currency(balance)
                if debit or credit:
                    self.table.insert('','end', values=values, tag='nominal' )
                ntotal['debit']+= debit
                ntotal['credit'] += credit
                ntotal['creditor'] += balance

            for account in db.query(Account).filter_by(content=Content.NOMINAL).filter_by(type=Type.DEBIT):
                debit = account.debit(year)
                credit = account.credit(year)
                balance = account.balance(year)
                values = account.gname, db_currency(debit), db_currency(credit), db_currency(balance), '-'
                if debit or credit :
                    self.table.insert('','end', values=values, tag='nominal' )
                ntotal['debit'] += debit
                ntotal['credit'] += credit
                ntotal['debtor'] += balance
                
        total = {
            'debit': rtotal['debit'] + ntotal['debit'],
            'credit': rtotal['credit'] + ntotal['credit'],
            'debtor': rtotal['debtor'] + ntotal['debtor'],
            'creditor': rtotal['creditor'] + ntotal['creditor']
        }
            
        if len(self.table.get_children()) > 1:                
            values = 'TOTAL', db_currency(total['debit']), db_currency(total['credit']),\
                db_currency(total['debtor']), db_currency(total['creditor'])            
            self.table.item(total_iid, values=values)

            if round(total['debit'],2)  != round(total['credit'],2): self.table.item(total_iid, tag='error')
            if round(total['debtor'],2) != round(total['creditor'],2): self.table.item(total_iid, tag='error')
        
            for n,iid in enumerate(self.table.get_children()):
                if iid == total_iid: continue
                if n%2 == 0:
                    if self.table.tag_has('real', iid) : self.table.item(iid, tag='even_real')
                    elif self.table.tag_has('nominal', iid): self.table.item(iid, tag='even_nominal')
        else:
            self.table.delete(*self.table.get_children())
            
    def refresh(self, year):
        self.display_data(year)
        
    def display_account(self, event):
        if iid := event.widget.focus():
            account_gname = event.widget.set(iid, column='account')
            try: code = db_get_account_code(account_gname)
            except: pass
            else:
                self.master.master.ledger.account.set(account_gname)
                self.master.master.ledger.render_filter()
                self.master.master.notebook.select(2)
        return 'break'

