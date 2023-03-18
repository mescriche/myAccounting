from tkinter import *
from tkinter import ttk
from dbase import db_session, db_currency, Account
from locale import currency

class LedgerView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.pack(fill='both', expand=True)
        self.text = Text(self)
        self.text.pack(fill='both', expand=True)
        self.text.tag_configure('account', background='blue')
        self.render()

    def render(self):
        self.text['state'] = 'normal'
        self.text.delete('1.0', 'end')
        self.text.insert(1.0, f"{'LEDGER BOOK':^112}")
        self.text.insert(2.0, f"{'':=^112}\n")
        with db_session() as db:
            for account in db.query(Account).all():
                if account.isEmpty: continue
                self.render_treeview(account)
                #self.render_text(account)
                self.text.insert('end', '\n')
        self.text['state'] = 'disabled'

    def render_treeview(self, account):
        self.text.insert('end', f"{account.gname:<112}", ('account'))
        self.text.insert('end', '\n')
        self.text.insert('end', f"{'':-^112}\n")
        columns = ('eid', 'tid', 'date', 'debit', 'credit', 'description')
        data = dict()
        data['eid'] = {'text':'Eid', 'width':25, 'anchor':'c'}
        data['tid'] = {'text':'Tid', 'width':25, 'anchor':'c'}
        data['date'] = {'text':'Date', 'width':100, 'anchor':'c'}
        data['debit'] = {'text':'Debit', 'width':80, 'anchor':'e'}
        data['credit'] = {'text':'Credit', 'width':80, 'anchor':'e'}
        data['description'] = {'text':'Description', 'width':470, 'anchor':'w'}
        
        table = ttk.Treeview(self.text, columns=columns, show='headings')
        self.text.window_create('end', window=table)

        for topic in columns:
            table.heading(topic, text=data[topic]['text'])
            table.column(topic, width=data[topic]['width'], anchor=data[topic]['anchor'])
        for entry in account.entries:
            values = entry.id, entry.transaction.id, entry.transaction.date, db_currency(entry.debit), \
                db_currency(entry.credit), entry.transaction.description
            table.insert('','end', values=values)
        else:
            table.config(height=len(account.entries))
            self.text.insert('end', f"\n{'':-^112}\n")
    def render_text(self, account):
        self.text.insert('end', f"{account.gname:<112}", ('account'))
        self.text.insert('end', '\n')
        self.text.insert('end', f"{'':-^112}\n")
        self.text.insert('end', f"| {'EId':>4} | {'TId':>4} | {'Date':^10} | {'Debit':^10} | {'Credit':^10} | {'Description':<55} |\n")
        self.text.insert('end', f"{'':-^112} \n")
        for entry in account.entries:
            line = f"| {entry.id:>4} | {entry.transaction.id:>4} | {entry.transaction.date} | {db_currency(entry.debit):>10} | {db_currency(entry.credit):>10} | {entry.transaction.description:<55} |\n"
            self.text.insert('end', line)
            self.text.insert('end', f"{'':-^112}\n")
        self.text.insert('end', '\n')        
