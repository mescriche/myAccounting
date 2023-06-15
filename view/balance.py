__author__ = 'Manuel Escriche'
from tkinter import *
from tkinter import ttk, messagebox
from dbase import db_session, db_currency, Account, Type, db_get_yearRange
from .transaction import DMBookEntry, DMTransaction, DMTransactionEncoder
from .report import ConceptTree
from locale import currency
from datetime import datetime
import os, json

class BalanceView(ttk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.parent = parent
        self.pack(fill='both', expand=True)

        self.eyear = IntVar()
        title_frame = ttk.Frame(self)
        title_frame.pack(expand=False, fill='x', pady=5, padx=5)
        title = f'BALANCE SHEET'
        ttk.Label(title_frame, text = '').pack(side='left', expand=True, fill='x')
        ttk.Label(title_frame, text = f"{title}").pack(side='left')
        year_frame = ttk.Frame(title_frame)
        year_frame.pack(side='left')
        ttk.Label(year_frame, text = f"{'YEAR: ':>10}").pack(side='left', ipadx=0, ipady=0)
        self.year_combo = ttk.Combobox(year_frame, state='readonly', width=5, textvariable=self.eyear, postcommand=self._get_year)
        self.year_combo.pack(side='left', ipadx=0, ipady=0)
        self.year_combo.bind('<<ComboboxSelected>>', self.render)
        self._get_year()
        self.year_combo.current(0)
        ttk.Label(title_frame, text = '').pack(side='left', expand=True, fill='x')
        ttk.Button(title_frame, text='Closing Seat', command=self.create_closing_opening_seat).pack(side='left')
        
        self.text = Text(self, wrap='word')
        self.text.pack(fill='both', expand=True)
        scroll_bar = Scrollbar(self.text)
        self.text.configure(yscrollcommand=scroll_bar.set)
        scroll_bar.config(command=self.text.yview)
        scroll_bar.pack(side='right', fill='y')

        pw = ttk.Panedwindow(self.text, orient=HORIZONTAL)
        self.text.window_create('end', window=pw)

        report_file = 'balance.json'
        DIR = os.path.dirname(os.path.realpath(__file__))
        with open(os.path.join(DIR, report_file)) as _file:
            self.balance_repo = json.load(_file)
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
    def _get_year(self):
        min_year,max_year = db_get_yearRange()
        values =[*range(max_year, min_year-1, -1)]
        self.year_combo['values'] = values
        
    def create_closing_opening_seat(self):
        def collect_codes(data:dict) -> list:
            codes = list()
            for k in data:
                if isinstance(data[k], dict):
                    codes.extend(collect_codes(data[k]))
                elif isinstance(data[k], list):
                    codes.extend(data[k])
            else: return codes
        year = self.eyear.get()
        closing_entries = list()
        opening_entries = list()
        assets_accounts = collect_codes(self.balance_repo['assets'])
        with db_session() as db:
            for code in assets_accounts:
                account = db.query(Account).filter_by(code=code).one()
                amount = account.balance(year)
                if amount > 0:
                    closing_entry = DMBookEntry(account=account.gname, type=Type.CREDIT, amount=amount)
                    closing_entries.append(closing_entry)
                    opening_entry = DMBookEntry(account=account.gname, type=Type.DEBIT, amount=amount)
                    opening_entries.append(opening_entry)
                    
        claims_accounts = collect_codes(self.balance_repo['claims'])
        with db_session() as db:
            for code in claims_accounts:
                account = db.query(Account).filter_by(code=code).one()
                amount = account.balance(year)
                if amount > 0:
                    closing_entry = DMBookEntry(account=account.gname, type=Type.DEBIT, amount=amount)
                    closing_entries.append(closing_entry)
                    opening_entry = DMBookEntry(account=account.gname, type=Type.CREDIT, amount=amount)
                    opening_entries.append(opening_entry)
                    
        ### create closing seat for running year
        date = datetime.strptime(f'31-12-{year}', '%d-%m-%Y').date()
        description = f"Balance closing seat for year {year}"
        _data = [DMTransaction(id=0, date=date, description=description, entries=closing_entries),]
        root_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        datafile_dir = os.path.join(root_dir, 'datafiles')
        _filename = os.path.join(datafile_dir, f'{year}_balance_closing_seat.json')
        with open(_filename, 'w') as _file:
            json.dump(_data, _file, cls=DMTransactionEncoder, indent=4)

        ### create opening seat for next year
        with db_session() as db:
            wealth_acc = db.query(Account).filter_by(code=10).one() # Wealth account
            outcome_acc = db.query(Account).filter_by(code=11).one() # Outcome account
            earnings = outcome_acc.balance(year)
            outcome_type = Type.DEBIT if earnings > 0 else Type.CREDIT
            wealth_type = Type.CREDIT if outcome_type == Type.DEBIT else Type.CREDIT
            opening_entries.append(DMBookEntry(account=outcome_acc.gname, type=outcome_type, amount=abs(earnings)))
            opening_entries.append(DMBookEntry(account=wealth_acc.gname,  type=wealth_type,  amount=abs(earnings)))
        
        year = year + 1
        date = datetime.strptime(f'1-1-{year}', '%d-%m-%Y').date()
        description = f"Balance opening seat for year {year}"
        _data = [DMTransaction(id=0, date=date, description=description, entries=opening_entries),]
        root_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        datafile_dir = os.path.join(root_dir, 'datafiles')
        _filename = os.path.join(datafile_dir, f'{year}_opening_seat.json')
        with open(_filename, 'w') as _file:
            json.dump(_data, _file, cls=DMTransactionEncoder, indent=4)        
        messagebox.showwarning( message=f"{year-1} Balance closing seat file and \n{year} Opening seat file  have been created ", parent = self )
        
    def refresh(self, year):
        min_year,max_year = db_get_yearRange()
        self.year_combo['values'] = values =[*range(max_year, min_year-1, -1)]
        self.eyear.set(year)
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
