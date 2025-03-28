__author__ = 'Manuel Escriche'
from tkinter import *
from tkinter import ttk, messagebox
from datamodel.accounts_tree import AccountsTree
from dbase import Transaction, db_session, Account, Type
from controller.utility import db_currency, db_get_yearRange
from controller.app_seats import create_income_closing_seat, create_year_seats, db_record_file
from datamodel.transaction import DMBookEntry, DMTransaction, DMTransactionEncoder
from datetime import datetime
import os, json

class IncomeView(ttk.Frame):
    def __init__(self, parent, user, acc_tree, **kwargs):
        super().__init__(parent, **kwargs)
        self.parent = parent
        self.pack(fill='both', expand=True)
        self.user = user
        self.acc_tree = acc_tree
        
        self.eyear = IntVar()
        min_year,max_year = db_get_yearRange()
        self.eyear.set(max_year)
        
        title_frame = ttk.Frame(self)
        title_frame.pack(expand=False, fill='x', pady=5, padx=5)
        title = f'INCOME STATEMENT'
        ttk.Button(title_frame, text='Refresh', command=self.render).pack(side='left')
        ttk.Label(title_frame, text = '').pack(side='left', expand=True, fill='x')
        ttk.Label(title_frame, text = f"{title}{'YEAR: ':>10}{max_year}").pack(side='left')
        ttk.Label(title_frame, text = '').pack(side='left', expand=True, fill='x')
        ttk.Button(title_frame, text='Closing Seat', command=self.create_income_closing_seat).pack(side='left')
        
        pw = ttk.Panedwindow(self, orient=HORIZONTAL)
        pw.pack(fill='both', expand=True)
        
        inframe = ttk.Labelframe(pw, text='Input', labelanchor='n')
        pw.add(inframe, weight=1)

        self.inputs = ttk.Treeview(inframe,selectmode='browse', show='tree headings')
        self.inputs.pack(expand=True, fill='both')
        self.inputs['columns'] = ('amount', 'percent')
        self.inputs.heading('#0', text='Topic')
        self.inputs.heading('amount', text='Amount(€)')
        self.inputs.heading('percent', text='%')
        self.inputs.column('amount', width=100, anchor='e')
        self.inputs.column('percent', width=50, anchor='e')
        self.inputs.tag_configure('head', background='lightgray')
        self.inputs.tag_configure('total', background='lightblue')
        self.inputs.bind('<<TreeviewSelect>>', self.expand_node)
        self.inputs.bind('<Double-1>', self.display_on_ledger)
        
        outframe = ttk.Labelframe(pw, text='Output', labelanchor='n')
        pw.add(outframe, weight=1)

        self.outputs = ttk.Treeview(outframe,selectmode='browse', show='tree headings')
        self.outputs.pack(expand=True, fill='both')
        self.outputs['columns'] = ('amount', 'percent')
        self.outputs.heading('#0', text='Topic')
        self.outputs.heading('amount', text='Amount(€)')
        self.outputs.heading('percent', text='%')
        self.outputs.column('amount', width=100, anchor='e')
        self.outputs.column('percent', width=50, anchor='e')
        self.outputs.tag_configure('head', background='lightgray')
        self.outputs.tag_configure('total', background='lightblue')
        self.outputs.bind('<<TreeviewSelect>>', self.expand_node)
        self.outputs.bind('<Double-1>', self.display_on_ledger)

        self.income = StringVar()
        bgcolor,fgcolor = 'lightblue','black'
        summary_frame = Frame(self, bg=bgcolor)
        summary_frame.pack(expand=False, fill='x', pady=5, padx=5)
        Label(summary_frame, bg=bgcolor, text = '').pack(side='left', expand=True, fill='x')
        Label(summary_frame, bg=bgcolor, fg=fgcolor, text = f"INCOME = ").pack(side='left')
        Label(summary_frame, bg=bgcolor, fg=fgcolor, textvariable=self.income ).pack(side='left')
        Label(summary_frame, bg=bgcolor, text = '').pack(side='left', expand=True, fill='x')
        self.render()

        
    def render(self, *args):
        year = self.eyear.get()
        self.inputs.delete(*self.inputs.get_children())
        self.outputs.delete(*self.outputs.get_children())

        with db_session() as db:
            node = self.acc_tree.find_node('input')
            codes = self.acc_tree.get_account_codes(node)
            accounts = db.query(Account).filter(Account.code.in_(codes)).all()
            in_total = sum(map(lambda account: account.balance(year), accounts))
            values = db_currency(in_total), ''
            p_iid = self.inputs.insert('','end', text=str(node), values=values, tag='head', open=True)
            
            for child in node.children:
                codes = self.acc_tree.get_account_codes(child)
                accounts = db.query(Account).filter(Account.code.in_(codes)).all()
                amount = sum(map(lambda account: account.balance(year), accounts))
                values = db_currency(amount), f'{amount/in_total:.0%}' if in_total != 0 else '-'
                self.inputs.insert(p_iid, 'end', text=str(child), values=values, tag='entry', open=True)

            ############
            node = self.acc_tree.find_node('output')
            codes = self.acc_tree.get_account_codes(node)
            accounts = db.query(Account).filter(Account.code.in_(codes)).all()
            out_total = sum(map(lambda account: account.balance(year), accounts))
            values = db_currency(out_total), ''
            p_iid=self.outputs.insert('','end', text=str(node), values=values, tag='head', open=True)
            
            for child in node.children:
                codes = self.acc_tree.get_account_codes(child)
                accounts = db.query(Account).filter(Account.code.in_(codes)).all()
                amount = sum(map(lambda account: account.balance(year), accounts))
                values = db_currency(amount), f'{amount/out_total:.0%}' if out_total != 0 else '-'
                self.outputs.insert(p_iid, 'end', text=str(child), values=values, tag='entry', open=True)
            
            ###########
        
        total = in_total - out_total
        self.income.set(f'{db_currency(total)}€')


    def expand_node(self, event):
        year = self.eyear.get()
        table = event.widget
        if iid := event.widget.focus():
            if table.get_children(iid):
                if table.item(iid, 'open'):
                    table.item(iid, open=False)
                else:
                    table.item(iid, open=True)
                return 'break'
            #######
            node_name = table.item(iid, 'text')
            if node := self.acc_tree.find_node(node_name):
                total = float(table.set(iid, 'amount').replace('.','').replace(',','.'))
                with db_session() as db:
                    for child in node.children:
                        codes = self.acc_tree.get_account_codes(child)
                        accounts = db.query(Account).filter(Account.code.in_(codes)).all()
                        amount = sum(map(lambda account: account.balance(year), accounts))
                        values = db_currency(amount), f'{amount/total:.0%}' if total != 0 else '-'
                        table.insert(iid, 'end', text=str(child), values=values, tag='entry', open=True)
        return 'break'
                
    def create_income_closing_seat(self):
        year = self.eyear.get()
        filename = create_income_closing_seat(year, self.user.user_dir)
        self.parent.master.log.print(f'{filename} created')
        filename = os.path.join(self.user.datafiles_dir, filename)
        try: n = db_record_file(filename)
        except Exception as e:
            print(e)
            return
        else:
            output = create_year_seats(year, self.user.user_dir)
            self.parent.master.log.print(f"{output['filename']} has been created with {output['n_records']} records")
            messagebox.showwarning(parent=self,
                message=f"{year} Income closing seat file and\n{year} year seats file\nhave been created\nAdditionally Income closing file has been applied")
            self.refresh(year)
            return
            
    def display_on_ledger(self, event):
        year = self.eyear.get()
        table = event.widget
        if iid := event.widget.focus():
            node_name = table.item(iid, 'text')
            if node := self.acc_tree.find_node(node_name):
                self.parent.master.ledger.clear_filter()
                self.parent.master.ledger.account.set(node.ext_name)
                self.parent.master.ledger.etrans_year.set(year)
                self.parent.master.ledger.render_filter()
                self.parent.master.notebook.select(2)
                return 'break'

