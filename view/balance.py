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
        
        pw = ttk.Panedwindow(self.text, orient=HORIZONTAL)
        pw.pack(fill='both', expand=False)

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
        self.assets.tag_configure('subtotal', background='lightblue')
        
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
        self.claims.tag_configure('subtotal', background='lightblue')

        report_file = 'balance.json'
        DIR = path.dirname(path.realpath(__file__))
        with open(path.join(DIR, report_file)) as _file:
            self.balance_repo = load(_file)
        
        #self.render()

    def render(self):
        self.assets.delete(*self.assets.get_children())
        self.claims.delete(*self.claims.get_children())
        n_assets, n_claims = 0,0
        with db_session() as db:
            assets = list(filter(lambda account: account.isAsset, db.query(Account).all()))

            liquid_assets = list(filter(lambda asset: asset.code in self.balance_repo['assets']['current'], assets))
            
            for asset in liquid_assets:
                self.assets.insert('', 'end', values=(asset.gname, db_currency(asset.balance)))
                n_assets += 1
            else:
                if len(liquid_assets) > 0:
                    self.assets.insert('', 'end',
                                       values=('Current:', db_currency(sum((asset.balance for asset in liquid_assets)))),
                                       tag='subtotal')
                    n_assets += 1                
            solid_assets =  list(filter(lambda asset: asset.code in self.balance_repo['assets']['fixed'], assets))
            for asset in solid_assets:
                self.assets.insert('', 'end', values=(asset.gname, db_currency(asset.balance)))
                n_assets +=1
            else:
                if len(solid_assets) > 0:
                    self.assets.insert('', 'end',
                                       values=('Fixed:', db_currency(sum((asset.balance for asset in solid_assets)))),
                                       tag='subtotal')
                    n_assets += 1
            
            #
            claims = list(filter(lambda account: account.isClaim, db.query(Account).all()))
            short_enforceable_claims = list(filter(lambda claim: claim.code in self.balance_repo['claims']['short_term'], claims))
            for claim in short_enforceable_claims:
                self.claims.insert('', 'end', values=(claim.gname, db_currency(claim.balance)))
                n_claims += 1
            else:
                if len(short_enforceable_claims) > 0:
                    self.claims.insert('', 'end', values=('Short Term:',
                                                          db_currency(sum((claim.balance for claim in short_enforceable_claims)))),
                                       tag='subtotal')
                    n_claims += 1
            long_enforceable_claims = list(filter(lambda claim: claim.code in self.balance_repo['claims']['long_term'], claims))
            for claim in long_enforceable_claims:
                self.claims.insert('', 'end', values=(claim.gname, db_currency(claim.balance)))
                n_claims += 1
            else:
                if len(long_enforceable_claims) > 0:
                    self.claims.insert('', 'end', values=('Long Term:',
                                                          db_currency(sum((claim.balance for claim in long_enforceable_claims)))),
                                       tag='subtotal')
                    n_claims += 1                
            no_enforceable_claims = list(filter(lambda claim:  claim.code in self.balance_repo['claims']['net_worth'], claims))
            for claim in no_enforceable_claims:
                self.claims.insert('', 'end', values=(claim.gname, db_currency(claim.balance)))
                n_claims += 1
            else:
                if len(no_enforceable_claims) > 0:
                    self.claims.insert('', 'end', values=('Net Worth:',
                                                          db_currency(sum((claim.balance for claim in no_enforceable_claims)))),
                                       tag='subtotal')
                    n_claims += 1              
            assets_total = sum((asset.balance for asset in assets))
            claims_total = sum((claim.balance for claim in claims))
            
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
        
