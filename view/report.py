from tkinter import *
from tkinter import ttk
from dbase import db_session, db_currency, Account

class ConceptTree(ttk.Treeview):
    def __init__(self, parent, concept, **kwargs):
        super().__init__(parent, **kwargs)
        self.concepts = concept
        self['columns'] = ('topic', 'amount', 'accounts', 'percent')
        self.heading('topic', text='Topic')
        self.heading('amount', text='Amount(€)')
        self.heading('percent', text='%')
    
    def nlines(self, data:dict) -> int:
        total = 0
        for key in data:
            value = data[key]
            if isinstance(value, dict):
                total += 1 + self.nlines(value)
            elif isinstance(value, list):
                total +=1
        else: return total
        
    def render(self, year, acc_operator):
        def render_tree(head:str, iid:str, data:dict, operation) -> float:
            total = 0
            for key in data:
                value = data[key]
                title = f'{head}.{key}' if head else f'{key}'
                #print(title)
                if isinstance(value, dict):
                    values = title.title(), ''
                    branch_id = self.insert(iid, 'end', values=values,  open=True)
                    branch_total = render_tree(title, branch_id, value, operation)
                    total += branch_total
                    values = title.replace('_',' ').title(), db_currency(branch_total), ''
                    self.item(branch_id, values=values, tag=title, open=True)
                elif isinstance(value, list):
                    accounts = map(lambda code: db.query(Account).filter_by(code=code).one(), value)
                    amount = sum(map(operation, accounts))
                    n = title.count('.')
                    values = '\t'*n + key.title(), db_currency(amount), str(value)
                    self.insert(iid, 'end', values=values, tag=title)
                    total += amount
            else: return total

        def item_value(iid) -> float:
            return float(self.item(iid)['values'][1].replace('.','').replace(',','.'))
        
        def percentage(f_iid=None):
            total = item_value(f_iid)
            for c_iid in self.get_children(f_iid):
                try: value = 100 * item_value(c_iid)/total
                except ZeroDivisionError: pass
                else: self.set(c_iid, column='percent', value=f'{value:.1f}')
                percentage(c_iid)
                
        with db_session() as db:
            #iid = self.insert('', 'end', values=('TOTAL', ''), tag='total')
            total = render_tree('', '', self.concepts, acc_operator )
            self.insert('','end', values=('TOTAL', db_currency(total)), tag='total')

        nrows = 1 + self.nlines(self.concepts)
        self.config(height=nrows)
        ####percentage
        t_iid = list(self.get_children())[-1]
        total = item_value(t_iid)
        for c_iid in list(self.get_children())[:-1]:
             try: value = 100 * item_value(c_iid)/total
             except ZeroDivisionError: pass
             else: self.set(c_iid, column='percent', value=f'{value:.1f}')
             percentage(c_iid)
        
    #def credit_render(self, year):
    #    self.render(year, lambda account:account.credit(year) - account.debit(year))

    #def debit_render(self, year):
    #    self.render(year, lambda account:account.debit(year) - account.credit(year))
        
    def balance_render(self, year):
        self.render(year, lambda account:account.balance(year))

        
