__author__ = 'Manuel Escriche'
from tkinter import *
from tkinter import ttk, messagebox
from dbase import db_get_accounts_gname, db_get_profile, Type, db_currency
from .excelreader import create_excel_reader
from dataclasses import asdict
from .transaction import DMBookEntry, DMTransaction, DMTransactionEncoder
import json, os

class ExcelViewer(ttk.Frame):
    def __init__(self, parent, filename, **kwargs):
        super().__init__(parent, **kwargs)
        self.pack(expand=True, fill='both')
        
        #self.tools_bar = ttk.Frame(parent.tools_bar)
        #self.tools_bar.pack(side='right', fill='x')
        
        #self.master_account = StringVar()
        #labelframe = ttk.Labelframe(self.tools_bar, text='Master Account')
        #labelframe.pack(side='left', ipady=7)
        #account = ttk.Combobox(labelframe, state='readonly', textvariable=self.master_account, width=30)
        #account.config(values=db_get_accounts_gname())
        #account.pack(side='right')

        
        self.filter_keyword = StringVar()
        filter_bar = ttk.Frame(self)
        filter_bar.pack(fill='x')
        labelframe = ttk.Labelframe(filter_bar, text='Filter')
        labelframe.pack(side='left', fill='x')
        self.keyword_wdgt = ttk.Combobox(labelframe, textvariable=self.filter_keyword, width=50)
        self.keyword_wdgt.bind('<<ComboboxSelected>>', self._set_filter_view)
        self.keyword_wdgt.pack(side='left')
        filter_btn = ttk.Button(labelframe, text='Filter', command=self._set_filter_view)
        filter_btn.pack(side='left')
        clear_filter_btn = ttk.Button(labelframe, text='Clear', command=self._clear_filter_view)
        clear_filter_btn.pack(side='left')

        self.filter_account = StringVar()
        labelframe = ttk.Labelframe(filter_bar, text='Apply to filter')
        labelframe.pack(side='right')
        account = ttk.Combobox(labelframe, state='readonly', textvariable=self.filter_account, width=30)
        account.config(values=db_get_accounts_gname())
        account.pack(side='left')
        account.bind('<<ComboboxSelected>>', self._apply_to_filter)
        
        self.table = ttk.Treeview(self, **kwargs)
        self.table.pack(side='bottom', expand=True, fill='both')
        xscroll_bar = Scrollbar(self.table, orient='horizontal')
        self.table.configure(xscrollcommand=xscroll_bar.set)
        xscroll_bar.config(command=self.table.xview)
        xscroll_bar.pack(side='bottom', fill='x')
        yscroll_bar = Scrollbar(self.table)
        self.table.configure(yscrollcommand=yscroll_bar.set)
        yscroll_bar.config(command=self.table.yview)
        yscroll_bar.pack(side='right', fill='y')

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
        self.table.tag_configure('master_account', background='lightsalmon')

        values = '', '', '', 'MASTER ACCOUNT'
        master_account_iid = self.table.insert('', 'end', values=values, tag='master_account')
        reader = create_excel_reader(filename)
        total = 0
        for n,item in enumerate(reader.data):
            values = item['vdate'].strftime("%d-%m-%Y"), item['amount'], '', item['comment']
            self.table.insert('', 'end', text=n, values=values)
            total += item['amount']
        else: self.table.set(master_account_iid, column='amount', value=db_currency(total))
        
        DIR = os.path.dirname(filename)
        basename, ext = os.path.splitext(reader.filename)
        basename += '.json'
        self.filename = os.path.join(DIR, basename) 
        self.items = [iid for iid in self.table.get_children()]
        
    def _apply_to_filter(self, *args):
        items = [iid for iid in self.table.get_children()]
        if len(items) < len(self.items):
            value = self.filter_account.get()
            for iid in items:
                self.table.set(iid, column='account', value=value)                
        
    def _clear_filter_view(self):
        self.filter_keyword.set('')
        for iid in self.items:
            self.table.move(iid, '', 0) #reattach
            
    def _set_filter_view(self, *args):
        keyword = self.filter_keyword.get()              
        if keyword not in self.keyword_wdgt['values']:
            add_on = (keyword,) if isinstance(self.keyword_wdgt['values'], tuple) else keyword
            self.keyword_wdgt['values'] += add_on
        for iid in self.table.get_children():
            comment = self.table.set(iid, column='description')
            if  keyword in comment: pass
            else: self.table.detach(iid)
        
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
    
    def _on_double_click(self, event):
        iid = event.widget.focus()
        region = self.table.identify_region(event.x, event.y)
        if region == 'cell':
            description = self.table.set(iid, column='description')
            self.filter_keyword.set(description)
        return 'break'
    
    def _on_account_selected(self, event):
        new_value = event.widget.get()
        iid = event.widget.editing_item_iid
        self.table.set(iid, column='account', value=new_value)
        event.widget.destroy()
        return 'break'
            
    def _on_focus_out(self, event):
        event.widget.destroy()
        return 'break'
    
    def save_to_file(self, filename=None):
        _filename = self.filename if not filename else filename
        if len(list(self.data())) > 0:
            with open(_filename, 'w') as _file:
                json.dump(self.data(), _file, cls=DMTransactionEncoder, indent=4)
        else:
            messagebox.showwarning(message = 'empty data list', parent = self )
            
    def data(self):
        self._data = list()
        self._clear_filter_view()
        master_account = ''
        for iid in self.table.get_children():
            if self.table.tag_has('master_account', iid):
                master_account = self.table.set(iid, column='account')
                break
        else: raise Exception('Missing master_account tag')
        
        if not master_account or master_account not in db_get_accounts_gname():
            #raise Exception('Master account missing, or not known')
            messagebox.showwarning( message = 'Master account missing or not know, \n please try it again', parent = self )
            return
        ma_type = master_account[1]
        for n,iid in enumerate(self.table.get_children()):
            if self.table.tag_has('master_account', iid): continue
            date = self.table.set(iid, column='date')
            description= self.table.set(iid, column='description')
            entry_account = self.table.set(iid, column='account')

            amount = float(self.table.set(iid, column='amount'))
            if ma_type == 'D':
                entry1_type = Type.DEBIT if amount > 0 else Type.CREDIT
            elif ma_type == 'C':
                entry1_type = Type.CREDIT if amount > 0 else Type.DEBIT
            else: raise Exception('Unknown entry type')
            if entry1_type == Type.DEBIT: entry2_type = Type.CREDIT
            elif entry1_type == Type.CREDIT: entry2_type = Type.DEBIT
            trans = DMTransaction(n, date, description,
                                  [DBookEntry(master_account, entry1_type, amount),
                                   DBookEntry(entry_account, entry2_type, amount)])
            if trans.validate():
                self._data.append(trans)
            else:
                print(f'transaction {trans} is not ready for recording')
                break
        else: yield from self._data

    def clean_up(self):
        for child in self.winfo_children():
            child.destroy()
        else: self.destroy()        
