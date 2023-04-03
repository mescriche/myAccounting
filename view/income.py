from tkinter import *
from tkinter import ttk
from dbase import db_session, db_currency, Account, db_get_yearRange
from .report import ConceptTree
from datetime import datetime
from os import path
from json import load

class IncomeView(ttk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.parent = parent
        self.pack(fill='both', expand=True)

        self.eyear = IntVar()
        self.title = Frame(self, background='green', bd=3)
        self.title.pack(expand=False, fill='x', pady=5, padx=5)
        title = f'INCOME STATEMENT'
        ttk.Label(self.title, text = f"{title:^62}").pack(expand=False, side='left')
        ttk.Label(self.title, text = f"{'YEAR: ':>10}").pack(side='left', ipadx=0, ipady=0)
        year_combo = ttk.Combobox(self.title, state='readonly', width=5, textvariable=self.eyear)
        year_combo.pack(side='left', ipadx=0, ipady=0)
        min_year,max_year = db_get_yearRange()
        values =[*range(max_year, min_year-1, -1)]
        year_combo['values'] = values
        year_combo.bind('<<ComboboxSelected>>', self.render)
        self.eyear.set(values[0])
        
        self.text = Text(self)
        self.text.pack(fill='both', expand=True)
        scroll_bar = Scrollbar(self.text)
        self.text.configure(yscrollcommand=scroll_bar.set)
        scroll_bar.config(command=self.text.yview)
        scroll_bar.pack(side='right', fill='y')

        self.text.tag_configure('title', background='blue')
        self.text.tag_configure('subtitle', background='light blue')
        self.text.tag_configure('total', background='purple')
        
        report_file = 'income.json'
        DIR = path.dirname(path.realpath(__file__))
        with open(path.join(DIR, report_file)) as _file:
            self.income_repo = load(_file)
        self.income_repo.pop('purpose')
        self.income_repo.pop('profile')
        
        columns = ('topic', 'amount', 'accounts')
        self.table = ConceptTree(self.text, self.income_repo, height=20, selectmode='browse', columns=columns, show='headings')
        self.text.window_create('end', window=self.table)
        self.table.heading('topic', text='Topic')
        self.table.column('topic', width=250, anchor='w')
        self.table.heading('amount', text='Amount(€)')
        self.table.column('amount', width=80, anchor='e')
        self.table['displaycolumns'] = ['topic','amount']
        self.table.tag_configure('revenues', background='lightblue')
        self.table.tag_configure('taxes', background='darksalmon')        
        self.table.tag_configure('insurance', background='coral')
        self.table.tag_configure('expenses', background='lightsalmon')
        self.table.tag_configure('total', background='lightgray')
        self.table.bind('<<TreeviewSelect>>', self.display_concept_items)
        
        self.render()
        
    def display_concept_items(self, event):
        print('display concept')
        year = self.eyear.get()
        min_date = datetime.strptime(f'01-01-{year}', "%d-%m-%Y").date()
        max_date = datetime.strptime(f'31-12-{year}', "%d-%m-%Y").date()
        if iid := event.widget.focus():
            concept = self.table.item(iid)['values'][0]
            if codes:= self.table.item(iid)['values'][2]:
                codes = eval(codes)
                with db_session() as db:
                    accounts = map(lambda code: db.query(Account).filter_by(code=code).one(), codes)
                    entries = (entry for account in accounts for entry in account.entries)
                    entries = filter(lambda x: x.transaction.date >= min_date and x.transaction.date <= max_date, entries)
                    entries = sorted(entries, key=lambda x:x.transaction.date)
                    entries = [entry.id for entry in entries]
                self.parent.master.ledger.render_entries(concept, entries)
                self.parent.master.notebook.select(2)
        return 'break'    

    def render(self, *args):
        year = self.eyear.get()
        self.text['state'] = 'normal'
        self.table.delete(*self.table.get_children())
        self.table.render(year)
        self.text['state'] = 'disabled'
