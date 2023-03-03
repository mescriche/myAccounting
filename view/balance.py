from tkinter import *
from tkinter import ttk
from dbase import db_session, db_currency, Asset, Claim
from locale import currency

class BalanceView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.pack(fill='both', expand=True)
        #self.text = Text(self)
        pw = ttk.Panedwindow(self, orient=HORIZONTAL)
        pw.pack(fill='both', expand=True)

        dbit_frame = ttk.Labelframe(pw, text='Assets', labelanchor='n')
        pw.add(dbit_frame, weight=1)
        columns = ('name', 'balance')
        self.assets = ttk.Treeview(dbit_frame, columns=columns, show='headings')
        self.assets.pack(fill='both', expand=True)
        self.assets.heading('name', text='Account')
        self.assets.column('name', width=150, anchor='w')
        self.assets.heading('balance', text='Amount(€)')
        self.assets.column('balance', width=50, anchor='e')
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
        self.claims.tag_configure('total', background='lightgray')
        
        self.render()

    def render(self):
        self.assets.delete(*self.assets.get_children())
        self.claims.delete(*self.claims.get_children())
        n_assets, n_claims = 0,0
        with db_session() as db:
            for asset in db.query(Asset).all():
                if asset.credit > 0 or asset.debit > 0 :
                    self.assets.insert('', 'end', values=(asset.gname, asset.balance))
                    n_assets += 1
            for claim in db.query(Claim).all():
                if claim.credit > 0 or claim.debit > 0 :
                    self.claims.insert('', 'end', values=(claim.gname, claim.balance))
                    n_claims += 1
            assets_total = sum((asset.balance for asset in db.query(Asset).all()))
            claims_total = sum((claim.balance for claim in db.query(Claim).all()))
            
        if n_assets > n_claims:
            while (n_claims < n_assets):
                self.claims.insert('', 'end', values=('',''))
                n_claims += 1
        if n_claims > n_assets:
            while (n_assets < n_claims):
                self.assets.insert('', 'end', values=('',''))
                n_assets += 1
            
        assets_balance = currency(assets_total, symbol=False, grouping=True)
        self.assets.insert('', 'end', values=('Total', assets_balance), tag='total')
        claims_balance = currency(claims_total, symbol=False, grouping=True)
        self.claims.insert('', 'end', values=('Total', claims_balance), tag='total')
        
