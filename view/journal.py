from tkinter import *
from tkinter import ttk
from dbase import db_session, db_currency, Transaction

class JournalView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.pack(fill='both', expand=True)
        self.text = Text(self)
        self.text.pack(fill='both', expand=True)
        self.text.tag_configure('transaction', background='blue', foreground='yellow', justify='left')
        self.text.tag_configure('account', background='blue')
        #self.journal.tag_bind('account', "<Button-1>" , self.account_in_ledger)
        self.render()
        
    def account_in_ledger(self, event):
        print('account_in_ledger')
        index = self.journal.index('@{},{}'.format(event.x, event.y))
        tag_indices = list(self.journal.tag_ranges('account'))
        for start, end in zip(*[iter(tag_indices)]*2):
            if self.journal.compare(start, '<=', index) and self.journal.compare(index, '<', end):
                account = self.journal.get(start, end)
                self.parent.select(1)
                break
        else:
            print('Account not found')
        
    def render(self):
        self.text['state'] = 'normal'
        self.text.delete('1.0', 'end')
        with db_session() as db:
            for trans in reversed(db.query(Transaction).all()):
                #self.render_text(trans)
                self.render_treeview(trans)
        self.text['state'] = 'disabled'
        
    def render_treeview(self, trans):
        trans_id = f"Transaction #{trans.id}"
        self.text.insert('end', f"{trans_id :=^70}", ('transaction'))
        self.text.insert('end', '\n')
        self.text.insert('end', f"Date: {trans.date:%d-%m-%Y}\n")
        self.text.insert('end', f"Description: {trans.description}\n")
        self.text.insert('end', f"{'':-^70} \n")
        columns = ('debit', 'account', 'credit')
        data = dict()
        data['debit'] = {'text':'Debit', 'width':90, 'anchor':'e'}
        data['account'] = {'text':'Account', 'width':300, 'anchor':'w'}        
        data['credit'] = {'text':'Credit', 'width':90, 'anchor':'e'}
        
        table = ttk.Treeview(self.text, columns=columns, show='headings')
        self.text.window_create('end', window=table)
        for topic in columns:
            table.heading(topic, text=data[topic]['text'])
            table.column(topic, width=data[topic]['width'], anchor=data[topic]['anchor'])
        else:
            table.tag_configure('total', background='lightblue')
            
        for entry in trans.entries:
            values = db_currency(entry.debit), entry.account.gname, db_currency(entry.credit)
            table.insert('','end', values=values)
        else:
            table.insert('','end', values=(db_currency(trans.debit), '', db_currency(trans.credit)), tag='total')
            table.config(height=1+len(trans.entries))
            self.text.insert('end', f"\n{'':-^70}\n")

            
    def render_text(self, trans):
        self.text.insert('end', '{:=^60} \n'.format(' Transaction #{} '.format(trans.id)), ('transaction'))
        self.text.insert('end', f"Date: {trans.date:%d-%m-%Y}\n")
        self.text.insert('end', f"Description: {trans.description}\n")
        self.text.insert('end', f"{'':-^60} \n")
        self.text.insert('end', F"| {'Debit':^10} | {'Account':^30} | {'Credit':^10} |\n")
        self.text.insert('end', f"{'':-^60}\n")
        for entry in trans.entries:
            self.text.insert('end', f"| {db_currency(entry.debit):>10} |" )
            self.text.insert('end', f" {entry.account.gname:<30} " , ('account'))
            self.text.insert('end', f"| {db_currency(entry.credit):>10} |\n" )
        else:
            self.text.insert('end', f"{'':-^60} \n")
            self.text.insert('end', f"| {db_currency(trans.debit):>10} | {' ':<30} | {db_currency(trans.credit):>10} |\n")
