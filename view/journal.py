__author__ = 'Manuel Escriche'
from tkinter import *
from tkinter import ttk
from dbase import db_session, db_currency, Transaction, db_get_yearRange, db_get_accounts_gname
from datetime import datetime

class JournalView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.pack(fill='both', expand=True)
        
        self.filter = LabelFrame(self, text='Filter')
        self.filter.pack(fill='x', expand=False)
        
        self.etrans_id = StringVar()
        frame = Frame(self.filter)
        frame.pack(side='left', padx=10)
        ttk.Label(frame, text='Trans Id:').pack(side='left', ipadx=2, ipady=2)
        id_entry = ttk.Entry(frame, textvariable=self.etrans_id, width=7)
        id_entry.pack(ipadx=2, ipady=2)
        id_entry.bind('<Return>', self.render_request)

        self.etrans_year = StringVar()
        frame = Frame(self.filter)
        frame.pack(side='left', padx=10)
        ttk.Label(frame, text='Year:').pack(side='left', ipadx=2, ipady=2)
        year_combo = ttk.Combobox(frame, state='readonly', width=5, textvariable=self.etrans_year)
        year_combo.pack(ipadx=2, ipady=2)
        min_year,max_year = db_get_yearRange()
        year_combo['values'] = [*range(max_year, min_year-1, -1)] + ['']
        year_combo.bind('<<ComboboxSelected>>', self.render_request)
        year_combo.current(0)

        self.etrans_date = StringVar()
        frame = Frame(self.filter)
        frame.pack(side='left', padx=10)
        ttk.Label(frame, text='Date:').pack(side='left', ipadx=2, ipady=2)
        date_entry = ttk.Entry(frame, textvariable=self.etrans_date, width=10)
        date_entry.pack(ipadx=2, ipady=2)
        date_entry.bind('<Return>', self.render_request)
        
        self.etrans_description = StringVar()
        frame = Frame(self.filter)
        frame.pack(side='left', padx=10)
        ttk.Label(frame, text='Description:').pack(side='left', ipadx=2, ipady=2)
        desc_entry = ttk.Entry(frame, textvariable=self.etrans_description, width=30)
        desc_entry.pack(ipadx=2, ipady=2)
        desc_entry.bind('<Return>', self.render_request)

        ttk.Button(self.filter, text='Filter', command=self.render_request).pack(side='left', padx=20,pady=2)
        ttk.Button(self.filter, text='Clear', command=self.clear_filter).pack(padx=0, pady=2)

            
        self.text = Text(self)
        self.text.pack(fill='both', expand=True)
        scroll_bar = Scrollbar(self.text)
        self.text.configure(yscrollcommand=scroll_bar.set)
        scroll_bar.config(command=self.text.yview)
        scroll_bar.pack(side='right', fill='y')
        self.text.tag_configure('transaction', background='blue', foreground='yellow', justify='left')
        self.text.tag_configure('account', background='blue')
        self.render_request()
        ## display last 20 transactions
        #with db_session() as db:
        #    query = db.query(Transaction).order_by(Transaction.id.desc()).limit(20)
        #    if items := [item.id for item in query]:
        #        items.reverse()
        #        self.render(items)

    def clear_filter(self, *args):
        self.etrans_id.set('')
        self.etrans_description.set('')
        #self.etrans_year.set('')
        self.etrans_date.set('')
        
    def render_request(self, *args):
        with db_session() as db:
            query = db.query(Transaction)
            if self.etrans_id.get():
                _id = self.etrans_id.get()
                query = query.filter(Transaction.id == _id)
            if self.etrans_description.get():
                description = self.etrans_description.get()
                query = query.filter(Transaction.description.contains(description))
            if self.etrans_year.get():
                year = self.etrans_year.get()
                min_date = datetime.strptime(f'01-01-{year}', "%d-%m-%Y").date()
                max_date = datetime.strptime(f'31-12-{year}', "%d-%m-%Y").date()
                query = query.filter(Transaction.date >= min_date).filter(Transaction.date <= max_date)    
            if self.etrans_date.get():
                _date = self.etrans_date.get()
                date = datetime.strptime(_date, "%d-%m-%Y").date()
                query = query.filter(Transaction.date == date)
            if items := [item.id for item in query]:
                self.render(items)
            else:
                self.text['state'] = 'normal'
                self.text.delete('1.0', 'end')
                msg = f'{"No Items Found": ^180}'
                label = Label(self.text, text=msg, background='dark red')
                self.text.window_create('end', window=label)
                self.text['state'] = 'disabled'
            
    def render(self, trans:list):
        self.text['state'] = 'normal'
        self.text.delete('1.0', 'end')
        with db_session() as db:
            for _id in reversed(trans):
                try: item = db.query(Transaction).get(_id)
                except Exception as e:
                    print(e)
                else: self.render_treeview(item)
        self.text['state'] = 'disabled'

    def render_treeview(self, trans):
        trans_id = f"Transaction #{trans.id}"
        trans_id = f"{trans_id: ^180}"
        label = Label(self.text, text=trans_id, background='dark cyan')
        self.text.window_create('end', window=label)
        self.create_popup_menu(label, trans.id)
        self.text.insert('end', f"\nDate: {trans.date:%d-%m-%Y}\n")
        self.text.insert('end', f"Description: {trans.description}\n")
        self.text.insert('end', f"{'':-^100} \n")
        columns = ('debit', 'account', 'credit')
        data = dict()
        data['debit'] = {'text':'Debit', 'width':100, 'anchor':'e'}
        data['account'] = {'text':'Account', 'width':400, 'anchor':'w'}        
        data['credit'] = {'text':'Credit', 'width':100, 'anchor':'e'}
        
        table = ttk.Treeview(self.text, columns=columns, show='headings')
        table.bind('<<TreeviewSelect>>', self.display_account)
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
            self.text.insert('end', f"\n{'':^70}\n")

    def create_popup_menu(self, widget, value):
        menu = Menu(widget)
        menu.add_command(label='Remove Transaction', command= lambda e=value: self.remove_transaction(e) )
        if self.text.tk.call('tk', 'windowingsystem') == 'aqua':
            widget.bind('<2>',         lambda e: menu.post(e.x_root, e.y_root))
            widget.bind('<Control-1>', lambda e: menu.post(e.x_root, e.y_root))
        else:
            widget.bind('<3>', lambda e: menu.post(e.x_root, e.y_root))

        
    def remove_transaction(self, trans_id):
        #print('remove_transaction:', trans_id)
        with db_session() as db:
            trans = db.query(Transaction).get(trans_id)
            for entry in trans.entries:
                db.delete(entry)
            else:
                db.delete(trans)
        self.master.master.event_generate("<<DataBaseContentChanged>>")
            
    def display_account(self, event):
        if iid := event.widget.focus():
            account_gname = event.widget.item(iid)['values'][1]
            print(account_gname)
            self.parent.master.ledger.account.set(account_gname)
            self.parent.master.ledger.render_filter()
            self.parent.master.notebook.select(2)
        return 'break'

