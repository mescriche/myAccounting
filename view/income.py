__author__ = 'Manuel Escriche'
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
        self.title = ttk.Frame(self)
        self.title.pack(expand=False, fill='x', pady=5, padx=5)
        title = f'INCOME STATEMENT'
        ttk.Label(self.title, text = f"{title:^62}").pack(expand=False, side='left')
        ttk.Label(self.title, text = f"{'YEAR: ':>10}").pack(side='left', ipadx=0, ipady=0)
        self.year_combo = ttk.Combobox(self.title, state='readonly', width=5, textvariable=self.eyear)
        self.year_combo.pack(side='left', ipadx=0, ipady=0)
        min_year,max_year = db_get_yearRange()
        values =[*range(max_year, min_year-1, -1)]
        self.year_combo['values'] = values
        self.year_combo.bind('<<ComboboxSelected>>', self.render)
        self.eyear.set(values[0])
        
        self.text = Text(self)
        self.text.pack(fill='both', expand=True)
        scroll_bar = Scrollbar(self.text)
        self.text.configure(yscrollcommand=scroll_bar.set)
        scroll_bar.config(command=self.text.yview)
        scroll_bar.pack(side='right', fill='y')

        pw = ttk.Panedwindow(self.text, orient=VERTICAL, width=425)
        self.text.window_create('end', window=pw)
        
        report_file = 'income.json'
        DIR = path.dirname(path.realpath(__file__))
        with open(path.join(DIR, report_file)) as _file:
            self.income_repo = load(_file)
        self.income_repo.pop('purpose')
        self.income_repo.pop('profile')
        
        inframe = ttk.Labelframe(pw, text='Inflows', labelanchor='n')
        pw.add(inframe, weight=1)
        self.inflow = ConceptTree(inframe, self.income_repo['inflows'], height=20, selectmode='browse', show='headings')
        self.inflow.pack()
        self.inflow.column('topic', width=250, anchor='w')
        self.inflow.column('amount', width=100, anchor='e')
        self.inflow.column('percent', width=50, anchor='e')
        self.inflow['displaycolumns'] = ['topic','amount', 'percent']
        self.inflow.tag_configure('revenues', background='lightblue')
        self.inflow.tag_configure('taxes', background='darksalmon')        
        self.inflow.tag_configure('insurance', background='coral')
        self.inflow.tag_configure('expenses', background='lightsalmon')
        self.inflow.tag_configure('total', background='lightgray')
        self.inflow.bind('<<TreeviewSelect>>', self.display_concept_items)

          
        outframe = ttk.Labelframe(pw, text='Outflows', labelanchor='n')
        pw.add(outframe, weight=1)
        self.outflow = ConceptTree(outframe, self.income_repo['outflows'], height=20, selectmode='browse', show='headings')
        self.outflow.pack()
        self.outflow.column('topic', width=250, anchor='w')
        self.outflow.column('amount', width=100, anchor='e')
        self.outflow.column('percent', width=50, anchor='e')
        self.outflow['displaycolumns'] = ['topic','amount', 'percent']
        self.outflow.tag_configure('revenues', background='lightblue')
        self.outflow.tag_configure('taxes', background='darksalmon')        
        self.outflow.tag_configure('insurance', background='coral')
        self.outflow.tag_configure('expenses', background='lightsalmon')
        self.outflow.tag_configure('total', background='lightgray')
        self.outflow.bind('<<TreeviewSelect>>', self.display_concept_items)

        self.summary = StringVar()
        labelframe = ttk.Frame(pw)
        pw.add(labelframe, weight=1)
        ttk.Label(labelframe, textvariable=self.summary, anchor='c').pack()
        self.render()
        
    def refresh(self, year):
        min_year,max_year = db_get_yearRange()
        self.year_combo['values'] = values =[*range(max_year, min_year-1, -1)]
        self.eyear.set(year)
        self.render()
        
    def render(self, *args):
        year = self.eyear.get()
        self.text['state'] = 'normal'
        self.inflow.delete(*self.inflow.get_children())
        self.inflow.balance_render(year)
        self.outflow.delete(*self.outflow.get_children())
        self.outflow.balance_render(year)
        
        t_iid = list(self.inflow.get_children())[-1]
        in_total = float(self.inflow.item(t_iid)['values'][1].replace('.','').replace(',','.'))
        t_iid = list(self.outflow.get_children())[-1]
        out_total = float(self.outflow.item(t_iid)['values'][1].replace('.','').replace(',','.'))
        net_income = db_currency(in_total - out_total)
        self.summary.set(f'NET INCOME  = {net_income:>10}')
        self.text['state'] = 'disabled'

    def display_concept_items(self, event):
        year = self.eyear.get()
        min_date = datetime.strptime(f'01-01-{year}', "%d-%m-%Y").date()
        max_date = datetime.strptime(f'31-12-{year}', "%d-%m-%Y").date()
        table = event.widget
        if iid := event.widget.focus():
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
                codes = map(lambda x: eval(table.set(x, column='accounts')), self.table.get_children(iid))
                codes = [item for code in codes for item in code]
                with db_session() as db:
                    accounts = map(lambda code: db.query(Account).filter_by(code=code).one(), codes)
                    entries = (entry for account in accounts for entry in account.entries)
                    entries = filter(lambda x: x.transaction.date >= min_date and x.transaction.date <= max_date, entries)
                    entries = sorted(entries, key=lambda x:x.transaction.date)
                    entries = [entry.id for entry in entries]
            concept = 'Income: ' + concept
            self.parent.master.ledger.render_entries(concept, entries)
            self.parent.master.notebook.select(2)                        
        return 'break'    

