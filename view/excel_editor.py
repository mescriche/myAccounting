__author__ = 'Manuel Escriche'
from tkinter import *
from tkinter import ttk, messagebox
from tkinter.simpledialog import Dialog
from dbase import db_get_accounts_gname, db_get_profile, Type, db_currency
from .excelreader import create_excel_reader
from dataclasses import asdict
from .transaction import DMBookEntry, DMTransaction, DMTransactionEncoder
import json, os, pickle, datetime

class ExcelEditor(Dialog):
    #errormessage = 'Not a Transaction'
    def __init__(self, master, filename, **kwargs):
        title = 'Excel Transactions Editor'
        self.trans_list = None
        self.filename = filename
        super().__init__(master, title)
        
    def body(self, master):
        frame = ttk.Frame(master)
        frame.pack(fill='x')

        self.master_account_view = StringVar()
        _labelframe = ttk.Labelframe(frame, text='Master Acc')
        _labelframe.pack(side='left', fill='x')
        macc_view = ttk.Combobox(_labelframe, textvariable=self.master_account_view, width=7)
        macc_view.pack(side='left', padx=10, pady=10)
        macc_view.config(values=['show', 'hide'])
        macc_view.current(0)
        macc_view.bind('<<ComboboxSelected>>', self._set_filter_view)
        
        labelframe = ttk.Labelframe(frame, text='Filter')
        labelframe.pack(side='left', fill='x')

        self.filter_account = StringVar()
        _labelframe = ttk.Labelframe(labelframe, text='Account')
        _labelframe.pack(side='left')
        account = ttk.Combobox(_labelframe, state='readonly', textvariable=self.filter_account, width=30)
        account.config(values= [''] + db_get_accounts_gname())
        account.pack(side='left')
        #account.bind('<<ComboboxSelected>>', self._apply_to_filter)
        
        self.filter_keyword = StringVar()
        _labelframe = ttk.Labelframe(labelframe, text='Description')
        _labelframe.pack(side='left', padx=10)
        self.keyword_wdgt = ttk.Combobox(_labelframe, textvariable=self.filter_keyword, width=50)
        #self.keyword_wdgt.bind('<<ComboboxSelected>>', self._set_filter_view)
        self.keyword_wdgt.pack(side='left')

        _frame = ttk.Frame(labelframe)
        filter_btn = ttk.Button(_frame, text='Filter', command=self._set_filter_view)
        filter_btn.pack(side='left')
        clear_filter_btn = ttk.Button(_frame, text='Clear', command=self._clear_filter_view)
        clear_filter_btn.pack(side='left')
        _frame.pack(side='left', padx=10)

        _labelframe = ttk.Labelframe(frame, text='View scope')
        ttk.Button(_labelframe, text='Apply', command=self._apply_to_view ).pack(ipady=0, pady=6, padx=10)
        _labelframe.pack(side='left', fill='x')

        
        self.table = ttk.Treeview(master)
        self.table.pack(expand=True, fill='both')
        self.table.config(selectmode='browse')
        self.table.config(show='headings')
        columns = ('date','amount', 'account', 'description')
        self.table.config(columns=columns)
        self.table.config(displaycolumns=columns)        
        self.table.heading('date', text='Date')
        self.table.heading('account', text='Account')
        self.table.heading('amount', text='Amount(€)')
        self.table.heading('description', text='Description')
        self.table.column('account', width=200, anchor='w')
        self.table.column('date', width=80, anchor='c')
        self.table.column('amount', width=80, anchor='e')
        self.table.column('description', width=850, anchor='w')
        self.table.bind('<<TreeviewSelect>>', self._account_edit)
        self.table.bind('<Double-1>', self._on_double_click)
        self.table.tag_configure('master_account', background='light sky blue')
        self.table.tag_configure('error', background='lightsalmon')

        restore_filename = self.filename.removesuffix('.xlsx') + '.pickle'
        if os.path.isfile(restore_filename):
            with open(restore_filename, 'rb') as f:
                data = pickle.load(f)
            for entry in data:
                if entry[3] == 'MASTER ACCOUNT':
                    self.master_account_iid = self.table.insert('','end', values=entry, tag='master_account')
                else:
                    self.table.insert('', 'end', values=entry)                
        else:    
            reader = create_excel_reader(self.filename)
            total = 0
            values = '', '', '', 'MASTER ACCOUNT'
            self.master_account_iid = self.table.insert('', 'end', values=values, tag='master_account')
            for n,item in enumerate(reader.data):
                values = item['vdate'].strftime("%d-%m-%Y"), item['amount'], '', item['comment']
                self.table.insert('', 'end', values=values)
                total += item['amount']
            else:
                self.table.set(self.master_account_iid, column='amount', value=db_currency(total))

        self.table.config(height=25)
        
        self.entry_iids = [iid for iid in self.table.get_children()]
        return self.table
        
    def buttonbox(self):
        control_bar = ttk.Frame(self)
        ttk.Label(control_bar, text='').pack(side='left', expand=True, fill='x')
        ttk.Button(control_bar, text="Cancel", width=10, command=self.cancel).pack(side='left', padx=5, pady=5)
        ttk.Label(control_bar, text='').pack(side='left', expand=True, fill='x')
        ttk.Button(control_bar, text="Save", width=10, command=self.save).pack(side='left', padx=5, pady=5)
        ttk.Label(control_bar, text='').pack(side='left', expand=True, fill='x')
        ttk.Button(control_bar, text="Accept", width=10, command=self.ok, default=ACTIVE).pack(side='left', padx=5, pady=5)
        ttk.Label(control_bar, text='').pack(side='left', expand=True, fill='x')
        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.cancel)
        control_bar.pack(fill='x')

    def validate(self):
        master_account = self.table.set(self.master_account_iid, column='account')
        if not master_account:
            self.table.see(iid)
            messagebox.showwarning(message= f'Missing Master account at row #{n+1}' + "\n Please, try again", parent=self)
            return False            
        for n,iid in enumerate(self.entry_iids):
            if iid == self.master_account_iid: continue
            self.table.item(iid, tags = ())
            self.table.see(iid)
            account = self.table.set(iid, column='account')
            if not account:
                self.table.item(iid, tag='error')
                messagebox.showwarning(message= f'Missing account at row #{n+1}' + "\n Please, try again", parent=self)
                return False
            if account == master_account:
                self.table.item(iid, tag='error')
                messagebox.showwarning(message=f'Account at row #{n+1} must be different to Master' + "\n Please, try again", parent = self)
                return False
            if account not in db_get_accounts_gname():
                self.table.item(iid, tag='error')
                messagebox.showwarning(message=f"Unknown account at row #{n+1}" + "\n Please, try again", parent=self)
                return False
            date = self.table.set(iid, column='date')
            if not date:
                self.table.item(iid, tag='error')
                messagebox.showwarning(message=f'Missing date at row #{n+1}' + "\n Please, try again", parent=self)
                return False
            try: date = datetime.datetime.strptime(date, "%d-%m-%Y").date()
            except ValueError:
                self.table.item(iid, tag='error')
                messagebox.showwarning(message=f'Wrong date value or format at row #{n+1}' + "\n Please, try again", parent=self)
                return False       
            amount = self.table.set(iid, column='amount')
            if not amount:
                self.table.item(iid, tag='error')
                messagebox.showwarning(message=f'Missing amount at row #{n+1}' + "\n Please, try again", parent=self)
                return False
            try: float(amount)
            except ValueError:
                self.table.item(iid, tag='error')
                messagebox.showwarning(mesage=f'Wrong amount or format at row #{n+1}' + "\n Please, try again", parent=self)
                return False
            description = self.table.set(iid, column='description')
            if not description:
                self.table.item(iid, tag='error')
                messagebox.showwarning(message=f'Missing description at row #{n+1}' + "\n Please, try again", parent=self)
                return False            
        return True

    def apply(self):
        self.save(show_msgbox=False)
        data = list()
        master_account = self.table.set(self.master_account_iid, column='account')
        macc_type = master_account[1]
        for n,iid in enumerate(self.entry_iids):
            if iid == self.master_account_iid: continue
            date, amount, account, description = self.table.item(iid)['values']
            date = datetime.datetime.strptime(date, "%d-%m-%Y").date()
            amount = float(amount)
            if macc_type == 'D':
                entry1_type = Type.DEBIT if amount > 0 else Type.CREDIT
            elif macc_type == 'C':
                entry1_type = Type.CREDIT if amount > 0 else Type.DEBIT
            else: raise Exception('Unknown entry type')
            entry2_type = Type.CREDIT if entry1_type == Type.DEBIT else Type.DEBIT
            amount = abs(amount)
            data.append(DMTransaction(id=n, date=date, description=description,
                                      entries = [DMBookEntry(master_account, entry1_type, amount),
                                                 DMBookEntry(account, entry2_type, amount)]))
        else:
            self.trans_list = data
        
    def save(self, show_msgbox=True):
        filename = self.filename.removesuffix('.xlsx') + '.pickle'
        data = [self.table.item(iid)['values'] for iid in self.entry_iids]
        with open(filename, 'wb') as f:
            # Pickle the 'data' dictionary using the highest protocol available.
            pickle.dump(data, f, pickle.HIGHEST_PROTOCOL)
        if show_msgbox:
            messagebox.showwarning(message='Sheet status saved', parent=self)

    def _apply_to_view(self, *args):
        items = [iid for iid in self.table.get_children()]
        if len(items) < len(self.entry_iids):
            value = self.table.set(items[0], column='account')
            for iid in items:
                self.table.set(iid, column='account', value=value)
                
    def _set_filter_view(self, event=None):
        keyword = self.filter_keyword.get()              
        if keyword not in self.keyword_wdgt['values']:
            add_on = (keyword,) if isinstance(self.keyword_wdgt['values'], tuple) else keyword
            self.keyword_wdgt['values'] += add_on

        account = self.filter_account.get()
        for iid in self.table.get_children():
            item_comment = self.table.set(iid, column='description')
            item_account = self.table.set(iid, column='account')
            if  keyword in item_comment and account == item_account: pass
            else: self.table.detach(iid)
            
        if self.master_account_view.get() == 'show':
            self.table.move(self.master_account_iid, '', 0)
        elif self.master_account_view.get() == 'hide':
            self.table.detach(self.master_account_iid)
        else: pass

    def _clear_filter_view(self):
        self.filter_keyword.set('')
        self.filter_account.set('')
        for iid in self.entries_iids:
            if iid != self.master_account_iid:
                self.table.move(iid, '', 0) #reattach
    
    def _account_edit(self, event):
        iid = event.widget.focus()
        column_box = self.table.bbox(event.widget.focus(), "2")
        account_edit = ttk.Combobox(self.table, state='readonly', width=column_box[2])
        account_edit.config(values=db_get_accounts_gname())
        account_edit.place(x=column_box[0], y=column_box[1], w=column_box[2], h=column_box[3])        
        account_edit.editing_item_iid = iid
        account_edit.focus()
        account_edit.bind('<FocusOut>', self._on_focus_out)
        account_edit.bind('<<ComboboxSelected>>', self._on_account_selected)
        return 'break'

    def _on_account_selected(self, event=None):
        new_value = event.widget.get()
        iid = event.widget.editing_item_iid
        self.table.set(iid, column='account', value=new_value)
        event.widget.destroy()
        return 'break'        
        
    def _on_focus_out(self, event=None):
        event.widget.destroy()
        return 'break'

    def _on_double_click(self, event):
        iid = event.widget.focus()
        region = self.table.identify_region(event.x, event.y)
        if region == 'cell':
            description = self.table.set(iid, column='description')
            self.filter_keyword.set(description)
        return 'break'
    
