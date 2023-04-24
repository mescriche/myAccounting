__author__ = 'Manuel Escriche'
from tkinter import *
from tkinter import ttk, messagebox
from dbase import db_session, db_currency, Account, Type, db_get_yearRange
from .transaction import DMBookEntry, DMTransaction, DMTransactionEncoder
from .report import ConceptTree
from datetime import datetime
import os, json

class IncomeView(ttk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.parent = parent
        self.pack(fill='both', expand=True)

        self.eyear = IntVar()
        title_frame = ttk.Frame(self)
        title_frame.pack(expand=False, fill='x', pady=5, padx=5)
        title = f'INCOME STATEMENT'
        ttk.Label(title_frame, text = '').pack(side='left', expand=True, fill='x')
        ttk.Label(title_frame, text = f"{title}").pack(side='left')
        year_frame = ttk.Frame(title_frame)
        year_frame.pack(side='left')
        ttk.Label(year_frame, text = f"{'YEAR: ':>10}").pack(side='left', ipadx=0, ipady=0)
        self.year_combo = ttk.Combobox(year_frame, state='readonly', width=5, textvariable=self.eyear)
        self.year_combo.pack(side='left', ipadx=0, ipady=0)
        min_year,max_year = db_get_yearRange()
        values =[*range(max_year, min_year-1, -1)]
        self.year_combo['values'] = values
        self.year_combo.bind('<<ComboboxSelected>>', self.render)
        self.eyear.set(values[0])
        ttk.Label(title_frame, text = '').pack(side='left', expand=True, fill='x')
        ttk.Button(title_frame, text='Closing Seat', command=self.create_income_closing_seat).pack(side='left')
        
        self.text = Text(self)
        self.text.pack(fill='both', expand=True)
        scroll_bar = Scrollbar(self.text)
        self.text.configure(yscrollcommand=scroll_bar.set)
        scroll_bar.config(command=self.text.yview)
        scroll_bar.pack(side='right', fill='y')

        pw = ttk.Panedwindow(self.text, orient=VERTICAL, width=425)
        self.text.window_create('end', window=pw)
        
        report_file = 'income.json'
        DIR = os.path.dirname(os.path.realpath(__file__))
        with open(os.path.join(DIR, report_file)) as _file:
            self.income_repo = json.load(_file)
        self.income_repo.pop('purpose')
        self.income_repo.pop('profile')
        
        inframe = ttk.Labelframe(pw, text='Inflows', labelanchor='n')
        pw.add(inframe, weight=1)
        self.inflow = ConceptTree(inframe, self.income_repo['inflows'],
                                  height=20, selectmode='browse', show='headings')
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
        self.outflow = ConceptTree(outframe, self.income_repo['outflows'],
                                   height=20, selectmode='browse', show='headings')
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
        in_total = float(self.inflow.set(t_iid, column='amount').replace('.','').replace(',','.'))
        t_iid = list(self.outflow.get_children())[-1]
        out_total = float(self.outflow.set(t_iid, column='amount').replace('.','').replace(',','.'))
        net_income = db_currency(in_total - out_total)
        self.summary.set(f'NET INCOME  = {net_income:>10}')
        self.text['state'] = 'disabled'

        
    def create_income_closing_seat(self):
        def collect_codes(data:dict) -> list:
            codes = list()
            for k in data:
                if isinstance(data[k], dict):
                    codes.extend(collect_codes(data[k]))
                elif isinstance(data[k], list):
                    codes.extend(data[k])
            else: return codes
            
        year = self.eyear.get()
        entries = list()
        in_accounts = collect_codes(self.income_repo['inflows'])
        with db_session() as db:
            total = 0
            for code in in_accounts:
                account = db.query(Account).filter_by(code=code).one()
                amount = account.credit(year)
                if amount > 0:
                    total += amount
                    entry = DMBookEntry(account=account.gname, type=Type.DEBIT, amount=amount)
                    entries.append(entry)
            else:
                ### Outcome (code=11)
                outcome_code = 11
                account = db.query(Account).filter_by(code=outcome_code).one()
                entry = DMBookEntry(account=account.gname, type=Type.CREDIT, amount=total)
                entries.append(entry)
                    
        out_accounts = collect_codes(self.income_repo['outflows'])
        with db_session() as db:
            total = 0
            for code in out_accounts:
                account = db.query(Account).filter_by(code=code).one()
                amount = account.debit(year)
                if amount > 0:
                    total += amount
                    entry = DMBookEntry(account=account.gname, type=Type.CREDIT, amount=amount)
                    entries.append(entry)
            else:
                outcome_code = 11
                account = db.query(Account).filter_by(code=outcome_code).one()
                entry = DMBookEntry(account=account.gname, type=Type.DEBIT, amount=total)
                entries.append(entry)
                    
        date = datetime.strptime(f'31-12-{year}', '%d-%m-%Y').date()
        description = f"Income closing seat for year {self.eyear.get()}"
        _data = [DMTransaction(id=0, date=date, description=description, entries=entries),]
        root_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        datafile_dir = os.path.join(root_dir, 'datafiles')
        _filename = os.path.join(datafile_dir, f'income_closing_seat_{self.eyear.get()}.json')
        with open(_filename, 'w') as _file:
            json.dump(_data, _file, cls=DMTransactionEncoder, indent=4)
        messagebox.showwarning( message=f"Income closing seat {year} has been created ", parent = self )

            
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

