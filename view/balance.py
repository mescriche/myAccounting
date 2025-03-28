__author__ = 'Manuel Escriche'
from tkinter import *
from tkinter import ttk, messagebox
from datamodel.accounts_tree import AccountsTree
from dbase import db_session, Account, Type
from controller.utility import db_currency, db_get_yearRange
from controller.app_seats import create_balance_closing_seat, db_record_file
from datamodel.transaction import DMBookEntry, DMTransaction, DMTransactionEncoder
from locale import currency
from datetime import datetime
import re

class BalanceView(ttk.Frame):
    def __init__(self, parent, user, acc_tree, **kwargs):
        super().__init__(parent, **kwargs)
        self.parent = parent
        self.pack(fill='both', expand=True)
        self.user = user
        self.acc_tree = acc_tree
        
        self.eyear = IntVar()
        min_year,max_year = db_get_yearRange()
        self.eyear.set(max_year)
        
        title_frame = ttk.Frame(self)
        title_frame.pack(expand=False, fill='x', pady=5, padx=5)
        title = f'BALANCE SHEET'
        
        ttk.Button(title_frame, text='Refresh', command=self.render).pack(side='left')
        ttk.Label(title_frame, text = '').pack(side='left', expand=True, fill='x')
        ttk.Label(title_frame, text = f"{title}{'YEAR: ':>10}{max_year}").pack(side='left', ipadx=0, ipady=0)
        ttk.Label(title_frame, text = '').pack(side='left', expand=True, fill='x')
        ttk.Button(title_frame, text='Closing Seat', command=self.create_closing_opening_seat).pack(side='left')
        
        pw = ttk.Panedwindow(self, orient=HORIZONTAL)
        pw.pack(fill='both', expand=True)
        
        dbit_frame = ttk.Labelframe(pw, text='Assets', labelanchor='n')
        pw.add(dbit_frame, weight=1)
        
        self.assets = ttk.Treeview(dbit_frame, selectmode='browse', show='tree headings')
        self.assets.pack(fill='both', expand=True)
        self.assets['columns']=('amount','percent')
        self.assets.heading('#0', text='Topic')
        self.assets.heading('amount', text='Amount(€)')
        self.assets.heading('percent', text='%')
        self.assets.column('amount', width=100, anchor='e')
        self.assets.column('percent', width=50, anchor='e')
        self.assets.tag_configure('head', background='green2')
        self.assets.tag_configure('total', background='lightgray')
        self.assets.tag_configure('current_assets', background='green1')
        self.assets.bind('<<TreeviewSelect>>', self.expand_node)
        self.assets.bind('<Double-1>', self.display_on_ledger)
        
        cdit_frame = ttk.Labelframe(pw, text='Claims', labelanchor='n')
        pw.add(cdit_frame, weight=1)
        self.claims = ttk.Treeview(cdit_frame, 
                                   selectmode='browse', show='tree headings')
        self.claims.pack(fill='both', expand=True)
        self.claims['columns']=('amount','percent')
        self.claims.heading('#0', text='Topic')
        self.claims.heading('amount', text='Amount(€)')
        self.claims.heading('percent', text='%')
        self.claims.column('amount', width=100, anchor='e')
        self.claims.column('percent', width=50, anchor='e') 
        self.claims.tag_configure('head', background='lightblue')
        self.claims.tag_configure('net_worth', background='gold')
        self.claims.tag_configure('total', background='lightgray')
        self.claims.bind('<<TreeviewSelect>>', self.expand_node)
        self.claims.bind('<Double-1>', self.display_on_ledger)
        self.render()
        

    def render(self, *args):
        year = self.eyear.get()
        self.assets.delete(*self.assets.get_children())
        self.claims.delete(*self.claims.get_children())
        
        with db_session() as db:
            node = self.acc_tree.find_node('assets')
            codes = self.acc_tree.get_account_codes(node)
            accounts = db.query(Account).filter(Account.code.in_(codes)).all()
            total = sum(map(lambda account: account.balance(year), accounts))
            values = db_currency(total), ''
            p_iid = self.assets.insert('','end', text=str(node), values=values, tag='head', open=True)
            for n,child in enumerate(node.children):
                codes = self.acc_tree.get_account_codes(child)
                accounts = db.query(Account).filter(Account.code.in_(codes)).all()
                amount = sum(map(lambda account: account.balance(year), accounts))
                values = db_currency(amount), f'{amount/total:.0%}' if total != 0 else '-'
                self.assets.insert(p_iid, 'end', text=str(child), values=values, tag='entry', open=True)
            ###########
            node = self.acc_tree.find_node('claims')
            codes = self.acc_tree.get_account_codes(node)
            accounts = db.query(Account).filter(Account.code.in_(codes)).all()
            total = sum(map(lambda account: account.balance(year), accounts))
            values = db_currency(total), ''
            
            p_iid = self.claims.insert('','end', text=str(node), values=values, tag='head', open=True)
            for n,child in enumerate(node.children):
                codes = self.acc_tree.get_account_codes(child)
                accounts = db.query(Account).filter(Account.code.in_(codes)).all()
                amount = sum(map(lambda account: account.balance(year), accounts))
                values = db_currency(amount), f'{amount/total:.0%}' if total != 0 else '-'
                self.claims.insert(p_iid, 'end', text=str(child), values=values, tag='entry', open=True)
            
    def expand_node(self, event):
        year = self.eyear.get()
        table = event.widget
        if iid := event.widget.focus():
            if table.get_children(iid):
                if table.item(iid, 'open'):
                    table.item(iid, open=False)
                else:
                    table.item(iid, open=True)
                return 'break'
            #######
            node_name = table.item(iid, 'text')
            if node := self.acc_tree.find_node(node_name):
                total = float(table.set(iid, 'amount').replace('.','').replace(',','.'))
                with db_session() as db:
                    for child in node.children:
                        codes = self.acc_tree.get_account_codes(child)
                        accounts = db.query(Account).filter(Account.code.in_(codes)).all()
                        amount = sum(map(lambda account: account.balance(year), accounts))
                        values = db_currency(amount), f'{amount/total:.0%}' if total != 0 else '-'
                        table.insert(iid, 'end', text=str(child), values=values, tag='entry', open=True)
        return 'break'       
        
    def display_on_ledger(self, event):
        year = self.eyear.get()
        table = event.widget
        if iid := event.widget.focus():
            node_name = table.item(iid, 'text')
            if node := self.acc_tree.find_node(node_name):
                self.parent.master.ledger.clear_filter()
                self.parent.master.ledger.account.set(node.ext_name)
                self.parent.master.ledger.etrans_year.set(year)
                self.parent.master.ledger.render_filter()
                self.parent.master.notebook.select(2)
                return 'break'

    def create_closing_opening_seat(self):
        year = self.eyear.get()
        outcome = create_balance_closing_seat(year, self.user.user_dir)
        c_filename = os.path.join(self.user.datafiles_dir, outcome['closing'])
        o_filename = os.path.join(self.user.datafiles_dir, outcome['opening'])
        try: n = db_record_file(c_filename)
        except Exception as e:
            print(e)
            return
        try: n = db_record_file(o_filename)
        except Exception as e:
            print(e)
            return
        messagebox.showwarning(parent=self,
                message=f"{year} Balance closing seat file and\n{year+1} Balance opening seat file \nhave been created\nBesides, {year + 1} Balance opening file has been applied")
        #self.refresh(year+1)
