from tkinter import *
from tkinter import ttk
from dbase import db_session, db_currency, Account

class ConceptTree(ttk.Treeview):
    def __init__(self, parent, concept, **kwargs):
        super().__init__(parent, **kwargs)
        self.concepts = concept
    
    def nlines(self, data:dict) -> int:
        total = 0
        for key in data:
            value = data[key]
            if isinstance(value, dict):
                total += 1 + self.nlines(value)
            elif isinstance(value, list):
                total +=1
        else: return total
        
    def render(self, year):
        def render_tree(head:str, iid:str, data:dict) -> float:
            total = 0
            for key in data:
                value = data[key]
                title = f'{head}.{key}' if head else f'{key}'
                print(title)
                if isinstance(value, dict):
                    values = title.title(), ''
                    branch_id = self.insert(iid, 'end', values=values,  open=True)
                    branch_total = render_tree(title, branch_id, value)
                    total += branch_total
                    values = title.replace('_',' ').title(), db_currency(branch_total), ''
                    self.item(branch_id, values=values, tag=title, open=True)
                elif isinstance(value, list):
                    accounts = map(lambda code: db.query(Account).filter_by(code=code).one(), value)
                    amount = sum(map(lambda account:account.balance(year), accounts))
                    #if title.count('.'): self.insert(_iid, 'end', values=('\t'*n + key.title(), db_currency(amount)))
                    n = title.count('.')
                    values = '\t'*n + key.title(), db_currency(amount), str(value)
                    self.insert(iid, 'end', values=values, tag=title)
                    total += amount
            else: return total

        with db_session() as db:
            total = render_tree('', '', self.concepts)
            self.insert('', 'end', values=('TOTAL', db_currency(total)), tag='total')

        nrows = 1 + self.nlines(self.concepts)
        self.config(height=nrows)


   
        
