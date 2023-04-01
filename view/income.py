from tkinter import *
from tkinter import ttk
from dbase import db_session, db_currency, Account, db_get_yearRange
from os import path
from json import load

class IncomeView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
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

        columns = ('topic', 'amount')
        self.table = ttk.Treeview(self.text, height=20, columns=columns, show='headings')
        self.text.window_create(3.10, window=self.table)
        
        self.table.heading('topic', text='Topic')
        self.table.column('topic', width=300, anchor='w')
        self.table.heading('amount', text='Amount(€)')
        self.table.column('amount', width=120, anchor='e')
        self.table.tag_configure('revenue', background='lightblue')
        self.table.tag_configure('expense', background='LightSalmon')
        self.table.tag_configure('total', background='lightgray')
        
        report_file = 'income.json'
        DIR = path.dirname(path.realpath(__file__))
        with open(path.join(DIR, report_file)) as _file:
            self.income_repo = load(_file)
            
        topics = ('revenues', 'expenses')            
        nrows = 1 + len(topics) + sum([len(self.income_repo[topic]) for topic in topics])
        self.table.config(height=nrows)
        self.render()
        
    def render(self, *args):
        year = self.eyear.get()
        self.text['state'] = 'normal'
        self.table.delete(*self.table.get_children())

        iid = self.table.insert('', 'end', values=('Revenue', ''), tag='revenue', open=True)
        rev_values = list()
        with db_session() as db:
            for revenue in self.income_repo['revenues']:
                codes = self.income_repo['revenues'][revenue]
                accounts = map(lambda code: db.query(Account).filter_by(code=code).one(), codes)
                value = sum(map(lambda account:account.balance(year), accounts))
                rev_values.append(value)
                self.table.insert(iid, 'end', values=(f"{'':8}{revenue.capitalize()}", db_currency(value)))
            else:
                self.table.item(iid, values=('Revenue', db_currency(sum(rev_values))))

        iid = self.table.insert('', 'end', values=('Expense', ''), tag='expense', open=True)
        exp_values = list()
        with db_session() as db:
            for expense in self.income_repo['expenses']:
                codes = self.income_repo['expenses'][expense]
                accounts = map(lambda code: db.query(Account).filter_by(code=code).one(), codes)
                value = sum(map(lambda account:account.balance(year), accounts))
                exp_values.append(value)
                self.table.insert(iid, 'end', values=(f"{'':8}{expense.capitalize()}", db_currency(value)))
            else:
                self.table.item(iid, values=('Expense', db_currency(sum(exp_values))))
        net_income = sum(rev_values) - sum(exp_values)
        self.table.insert('','end', values=('Net Income',db_currency(net_income)), tag='total')
        self.text['state'] = 'disabled'
        
    def render_text(self):
        self.text['state'] = 'normal'
        self.text.delete('1.0', 'end')
        self.text.insert('end', f"{'INCOME STATEMENT':^60}\n")
        self.text.insert('end', f"{'':=^60}\n")
        self.text.insert('end', f"{'Revenues:':<60}", ('title'))
        self.text.insert('end', '\n')
        self.text.insert('end', f"{'':-^60}\n")
        rev_total = list()
        for revenue in self.income_repo['revenues']:
            with db_session() as db:
                codes = self.income_repo['revenues'][revenue]
                accounts = map(lambda code:db.query(Account).filter_by(code=code).one(), codes)
                value = sum(map(lambda account:account.credit, accounts))
                rev_total.append(value)
            self.text.insert('end', f"\t{revenue.capitalize():<35}{db_currency(value):>10}\n")
        else:
            rev_total = sum(rev_total)
            self.text.insert('end', f"\t{'':-^45}\n")
            self.text.insert('end', f"\t{'Total':<35}{db_currency(rev_total):>10}\n")
        self.text.insert('end', '\n')
        self.text.insert('end', f"{'Expenses:':60}", ('title'))
        self.text.insert('end', '\n')
        self.text.insert('end', f"{'':-^60}\n")
        exp_total = list()
        for expense in self.income_repo['expenses']:
            with db_session() as db:
                codes = self.income_repo['expenses'][expense]
                accounts = map(lambda code: db.query(Account).filter_by(code=code).one(), codes)
                value = sum(map(lambda account:account.debit, accounts))
                exp_total.append(value)
            self.text.insert('end', f"\t{expense.capitalize():<35}{db_currency(value):>10}\n")
        else:
            exp_total = sum(exp_total)
            self.text.insert('end', f"\t{'':-^45}\n")
            self.text.insert('end', f"\t{'Total':<35}{db_currency(exp_total):>10}\n")
        total = rev_total - exp_total
        self.text.insert('end', '\n')
        self.text.insert('end', f"{'Net Income':<43}{db_currency(total):>10}{'':7}", ('total'))
        self.text.insert('end', '\n')
        self.text.insert('end', f"{'':=^60}\n")
        self.text['state'] = 'disabled'
