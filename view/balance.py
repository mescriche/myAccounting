__author__ = 'Manuel Escriche'
from tkinter import *
from tkinter import ttk
from dbase import db_session, db_currency, Account, db_get_yearRange
from .report import ConceptTree
from locale import currency
from datetime import datetime
from os import path
from json import load

class BalanceView(ttk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.parent = parent
        self.pack(fill='both', expand=True)

        self.eyear = IntVar()
        self.title = Frame(self, background='green', bd=3)
        self.title.pack(expand=False, fill='x', pady=5, padx=5)
        title = f'BALANCE SHEET'
        ttk.Label(self.title, text = f"{title:^157}").pack(expand=False, side='left')
        ttk.Label(self.title, text = f"{'YEAR: ':>10}").pack(side='left', ipadx=0, ipady=0)
        year_combo = ttk.Combobox(self.title, state='readonly', width=5, textvariable=self.eyear)
        year_combo.pack(side='left', ipadx=0, ipady=0)
        min_year,max_year = db_get_yearRange()
        values =[*range(max_year, min_year-1, -1)]
        year_combo['values'] = values
        year_combo.bind('<<ComboboxSelected>>', self.render)
        self.eyear.set(values[0])
        
        
        self.text = Text(self, wrap='word')
        self.text.pack(fill='both', expand=True)
        scroll_bar = Scrollbar(self.text)
        self.text.configure(yscrollcommand=scroll_bar.set)
        scroll_bar.config(command=self.text.yview)
        scroll_bar.pack(side='right', fill='y')

        pw = ttk.Panedwindow(self.text, orient=HORIZONTAL)
        self.text.window_create('end', window=pw)

        report_file = 'balance.json'
        DIR = path.dirname(path.realpath(__file__))
        with open(path.join(DIR, report_file)) as _file:
            self.balance_repo = load(_file)
        self.balance_repo.pop('purpose')
        self.balance_repo.pop('profile')
        
        dbit_frame = ttk.Labelframe(pw, text='Assets', labelanchor='n')
        pw.add(dbit_frame, weight=1)
        self.assets = ConceptTree(dbit_frame, self.balance_repo['assets'], selectmode='browse', show='headings')
        self.assets.pack(fill='both', expand=True)
        self.assets.column('topic', width=250, anchor='w')
        self.assets.column('amount', width=100, anchor='e')
        self.assets.column('percent', width=50, anchor='e')
        self.assets['displaycolumns'] = ['topic', 'amount', 'percent']
        self.assets.tag_configure('fixed_assets', background='green2')
        self.assets.tag_configure('current_assets', background='green1')
        self.assets.tag_configure('total', background='lightgray')
        self.assets.bind('<<TreeviewSelect>>', self.display_concept_items)
        
        cdit_frame = ttk.Labelframe(pw, text='Claims', labelanchor='n')
        pw.add(cdit_frame, weight=1)
        self.claims = ConceptTree(cdit_frame, self.balance_repo['claims'], selectmode='browse', show='headings')
        self.claims.pack(fill='both', expand=True)
        self.claims.column('topic', width=250, anchor='w')
        self.claims.column('amount', width=100, anchor='e')
        self.claims.column('percent', width=50, anchor='e') 
        self.claims['displaycolumns'] = ['topic', 'amount', 'percent']
        self.claims.tag_configure('short_term_debt', background='lightblue')
        self.claims.tag_configure('long_term_debt', background='lightblue1')
        self.claims.tag_configure('net_worth', background='gold')
        self.claims.tag_configure('total', background='lightgray')
        self.claims.bind('<<TreeviewSelect>>', self.display_concept_items)        
        self.render()

    def render(self, *args):
        year = self.eyear.get()
        self.text['state'] = 'normal'
        self.assets.delete(*self.assets.get_children())
        self.claims.delete(*self.claims.get_children())
        self.assets.balance_render(year)
        self.claims.balance_render(year)
        self.text['state'] = 'disabled'
        
    def display_concept_items(self, event):
        year = self.eyear.get()
        min_date = datetime.strptime(f'01-01-{year}', "%d-%m-%Y").date()
        max_date = datetime.strptime(f'31-12-{year}', "%d-%m-%Y").date()
        if iid := event.widget.focus():
            table = event.widget
            concept = table.set(iid, column='topic').replace('\t','')
            if codes:= table.set(iid, column='accounts'):
                codes = eval(codes)
                with db_session() as db:
                    accounts = map(lambda code: db.query(Account).filter_by(code=code).one(), codes)
                    entries = (entry for account in accounts for entry in account.entries)
                    entries = filter(lambda x: x.transaction.date >= min_date and x.transaction.date <= max_date, entries)
                    entries = sorted(entries, key=lambda x:x.transaction.date)
                    entries = [entry.id for entry in entries]
            else:
                codes = map(lambda x: eval(table.set(x, column='accounts')), table.get_children(iid))
                codes = [item for code in codes for item in code]
                with db_session() as db:
                    accounts = map(lambda code: db.query(Account).filter_by(code=code).one(), codes)
                    entries = (entry for account in accounts for entry in account.entries)
                    entries = filter(lambda x: x.transaction.date >= min_date and x.transaction.date <= max_date, entries)
                    entries = sorted(entries, key=lambda x:x.transaction.date)
                    entries = [entry.id for entry in entries]
            concept = 'Balance: ' + concept
            self.parent.master.ledger.render_entries(concept, entries)
            self.parent.master.notebook.select(2)   
        return 'break'   
