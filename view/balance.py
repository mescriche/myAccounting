__author__ = 'Manuel Escriche'
from tkinter import *
from tkinter import ttk, messagebox
from dbase import db_session, Account, Type
from controller.utility import db_currency, db_get_yearRange
from controller.app_seats import create_app_balance_closing_seat, db_record_file
from datamodel.transaction import DMBookEntry, DMTransaction, DMTransactionEncoder
from .report import ConceptTree
from locale import currency
from datetime import datetime
import os, json

class BalanceView(ttk.Frame):
    def __init__(self, parent, user_dir, **kwargs):
        super().__init__(parent, **kwargs)
        self.parent = parent
        self.pack(fill='both', expand=True)
        self.user_dir = user_dir
        self.configfiles_dir = os.path.join(user_dir, 'configfiles')
        self.datafiles_dir = os.path.join(user_dir, 'datafiles')
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
        with open(os.path.join(self.configfiles_dir, report_file)) as _file:
            self.balance_repo = json.load(_file)
        
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
        year = self.eyear.get()
        outcome = create_app_balance_closing_seat(year, self.user_dir)
        c_filename = os.path.join(self.datafiles_dir, outcome['closing'])
        o_filename = os.path.join(self.datafiles_dir, outcome['opening'])
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
        self.refresh(year+1)
            
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
