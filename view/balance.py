from tkinter import *
from tkinter import ttk
from dbase import db_session, db_currency, Account
from locale import currency
from os import path
from json import load

class BalanceView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.pack(fill='both', expand=True)
        self.text = Text(self, wrap='word')
        self.text.pack(fill='both', expand=True)
        
        self.text.insert(1.0, f"{'BALANCE SHEET':^80}\n")
        self.text.insert(2.0, f"{'':=^80}\n")
        
        pw = ttk.Panedwindow(self.text, orient=HORIZONTAL, width=560)
        self.text.window_create(3.0, window=pw)
        
        dbit_frame = ttk.Labelframe(pw, text='Assets', labelanchor='n')
        pw.add(dbit_frame, weight=1)
        columns = ('name', 'balance')
        self.assets = ttk.Treeview(dbit_frame, columns=columns, show='headings')
        self.assets.pack(fill='both', expand=True)
        self.assets.heading('name', text='Account')
        self.assets.column('name', width=150, anchor='w')
        self.assets.heading('balance', text='Amount(€)')
        self.assets.column('balance', width=50, anchor='e')
        self.assets.tag_configure('title', background='lightgreen')
        self.assets.tag_configure('total', background='lightgray')
        
        cdit_frame = ttk.Labelframe(pw, text='Claims', labelanchor='n')
        pw.add(cdit_frame, weight=1)
        columns = ('name', 'balance')
        self.claims = ttk.Treeview(cdit_frame, columns=columns, show='headings')
        self.claims.pack(fill='both', expand=True)
        self.claims.heading('name', text='Account')
        self.claims.column('name', width=150, anchor='w')
        self.claims.heading('balance', text='Amount(€)')
        self.claims.column('balance', width=50, anchor='e')
        self.claims.tag_configure('title', background='lightblue')
        self.claims.tag_configure('total', background='lightgray')

        
        report_file = 'balance.json'
        DIR = path.dirname(path.realpath(__file__))
        with open(path.join(DIR, report_file)) as _file:
            self.balance_repo = load(_file)
        
        self.render()

    def render(self):
        self.text['state'] = 'normal'
        #self.text.delete(1.0, 'end')
        #self.text.insert(1.0, f"{'BALANCE SHEET':^80}\n")
        #self.text.insert(2.0, f"{'':=^80}\n")
        self.assets.delete(*self.assets.get_children())
        self.claims.delete(*self.claims.get_children())
        
        ### ASSETS
        iid = self.assets.insert('','end', values=('Current',''), tag='title', open=True)
        c_values = list()
        with db_session() as db:
            for asset in self.balance_repo['assets']['current']:
                codes = self.balance_repo['assets']['current'][asset]
                accounts = map(lambda code:db.query(Account).filter_by(code=code).one(), codes)
                value = sum(map(lambda account: account.balance, accounts))
                c_values.append(value)
                self.assets.insert(iid, 'end', values=(f"{'':4}{asset.capitalize()}", db_currency(value)))                
            else:
                #self.assets.insert(iid, 'end', values=(f"{'':4}Total", db_currency(sum(c_values))), tag='subtotal')
                self.assets.item(iid, values=('Current', db_currency(sum(c_values))))
        
        iid = self.assets.insert('','end', values=('Fixed',''), tag='title', open=True)
        f_values = list()
        with db_session() as db:
            for asset in self.balance_repo['assets']['fixed']:
                codes = self.balance_repo['assets']['fixed'][asset]
                accounts = map(lambda code:db.query(Account).filter_by(code=code).one(), codes)
                value = sum(map(lambda account: account.balance, accounts))
                f_values.append(value)                
                self.assets.insert(iid, 'end', values=(f"{'':4}{asset.capitalize()}", db_currency(value)))
            else:
                #self.assets.insert(iid, 'end', values=(f"{'':4}Total", db_currency(sum(f_values))), tag='subtotal')
                self.assets.item(iid, values=('Fixed', db_currency(sum(f_values))))
        values = c_values + f_values
        self.assets.insert('', 'end', values=(f"TOTAL", db_currency(sum(values))), tag='total')

        ### CLAIMS
        
        iid = self.claims.insert('','end', values=('Short Term',''), tag='title', open=True)
        st_values = list()
        with db_session() as db:
            for claim in self.balance_repo['claims']['short_term']:
                codes = self.balance_repo['claims']['short_term'][claim]
                accounts = map(lambda code:db.query(Account).filter_by(code=code).one(), codes)
                value = sum(map(lambda account: account.balance, accounts))
                st_values.append(value)
                self.claims.insert(iid, 'end', values=(f"{'':4}{claim.capitalize()}", db_currency(value)))                
            else:
                #self.claims.insert(iid, 'end', values=(f"{'':4}Total", db_currency(sum(st_values))), tag='subtotal')
                self.claims.item(iid, values=('Short Term', db_currency(sum(st_values))))

        iid = self.claims.insert('','end', values=('Long Term',''), tag='title', open=True)
        lt_values = list()
        with db_session() as db:
            for claim in self.balance_repo['claims']['long_term']:
                codes = self.balance_repo['claims']['long_term'][claim]
                accounts = map(lambda code:db.query(Account).filter_by(code=code).one(), codes)
                value = sum(map(lambda account: account.balance, accounts))
                lt_values.append(value)
                self.claims.insert(iid, 'end', values=(f"{'':4}{claim.capitalize()}", db_currency(value)))                
            else:
                #self.claims.insert(iid, 'end', values=(f"{'':4}Total", db_currency(sum(st_values))), tag='subtotal')
                self.claims.item(iid, values=('Long Term', db_currency(sum(lt_values))))


        iid = self.claims.insert('','end', values=('Net Worth',''), tag='title', open=True)
        nw_values = list()
        with db_session() as db:
            for claim in self.balance_repo['claims']['net_worth']:
                codes = self.balance_repo['claims']['net_worth'][claim]
                accounts = map(lambda code:db.query(Account).filter_by(code=code).one(), codes)
                value = sum(map(lambda account: account.balance, accounts))
                nw_values.append(value)
                self.claims.insert(iid, 'end', values=(f"{'':4}{claim.capitalize()}", db_currency(value)))                
            else:
                #self.claims.insert(iid, 'end', values=(f"{'':4}Total", db_currency(sum(st_values))), tag='subtotal')
                self.claims.item(iid, values=('Net Worth', db_currency(sum(nw_values))))

        values = st_values + lt_values + nw_values
        self.claims.insert('', 'end', values=(f"TOTAL", db_currency(sum(values))), tag='total')
        
        self.text['state'] = 'disabled'
