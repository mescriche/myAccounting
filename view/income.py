from tkinter import *
from tkinter import ttk
from dbase import db_session, db_currency, Account
from os import path
from json import load

class IncomeView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.pack(fill='both', expand=True)
        self.text = Text(self)
        self.text.pack(fill='both', expand=True)
        self.text.tag_configure('title', background='blue')
        self.text.tag_configure('subtitle', background='light blue')
        self.text.tag_configure('total', background='purple')
        report_file = 'income.json'
        DIR = path.dirname(path.realpath(__file__))
        with open(path.join(DIR, report_file)) as _file:
            self.income_repo = load(_file)
        self.render()

    def render(self):
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
