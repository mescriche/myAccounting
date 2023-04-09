__author__ = 'Manuel Escriche'
from tkinter import *
from tkinter import ttk
from dbase import db_get_accounts_gname, db_get_profile
from .excelreader import create_excel_reader
from dataclasses import asdict
from .transaction import DBookEntry, DTransaction
import json, os

class ExcelViewer(ttk.Frame):
    def __init__(self, parent, filename, **kwargs):
        super().__init__(parent, **kwargs)
        self.pack(expand=True, fill='both')
        
        control_bar = ttk.Frame(self)
        control_bar.pack(expand=False, fill='x')
        self.master_account = StringVar()
        labelframe = ttk.Labelframe(control_bar, text='Master Account')
        labelframe.pack(side='left')
        account = ttk.Combobox(labelframe, state='readonly', textvariable=self.master_account)
        account.config(values=db_get_accounts_gname())
        account.pack(side='left', expand=False)

        self.filter_keyword = StringVar()
        labelframe = ttk.Labelframe(control_bar, text='Filter by description')
        labelframe.pack(side='left')
        self.keyword_wdgt = ttk.Combobox(labelframe, textvariable=self.filter_keyword, width=50)
        self.keyword_wdgt.bind('<<ComboboxSelected>>', self._set_filter_view)
        self.keyword_wdgt.pack(side='left', expand=False)
        filter_btn = ttk.Button(labelframe, text='Filter', command=self._set_filter_view)
        filter_btn.pack(side='left', expand=False)
        clear_filter_btn = ttk.Button(labelframe, text='Clear', command=self._clear_filter_view)
        clear_filter_btn.pack(side='left', expand=False)

        self.filter_account = StringVar()
        labelframe = ttk.Labelframe(control_bar, text='Apply to filter')
        labelframe.pack(side='left')
        account = ttk.Combobox(labelframe, state='readonly', textvariable=self.filter_account)
        account.config(values=db_get_accounts_gname())
        account.pack(side='left', expand=True)
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
        
        reader = create_excel_reader(filename)
        for n,item in enumerate(reader.data):
            values = str(item['vdate']), item['amount'], '', item['comment']
            self.table.insert('', 'end', text=n, values=values)
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
    
    def save_to_file(self):
        with open(self.filename, 'w') as _file:
            data = list(map(lambda x:asdict(x), self.data()))
            json.dump(data, _file, indent=4)
        #print(json.dumps(data,indent=4))
            
    def data(self):
        self._data = list()
        self._clear_filter_view()
        master_account = self.master_account.get()
        try:
            ma_type = master_account[1]
        except IndexError:
            raise Exception('Master Account missing')
        else:
            for iid in self.table.get_children():
                date = self.table.set(iid, column='date')
                description= self.table.set(iid, column='description')
                entry_account = self.table.set(iid, column='account')
                if not entry_account: raise Exception('Entry Account missing')
                amount = float(self.table.set(iid, column='amount'))
                if ma_type == 'D':
                    entry1_type = 'DEBIT' if amount > 0 else 'CREDIT'
                elif ma_type == 'C':
                    entry1_type = 'CREDIT' if amount > 0 else 'DEBIT'
                else: raise Exception('unknown account type')
                if entry1_type == 'DEBIT': entry2_type = 'CREDIT'
                elif entry1_type == 'CREDIT': entry2_type = 'DEBIT'
                amount = abs(amount)
                trans = DTransaction(date, description,
                                     [DBookEntry(master_account, entry1_type, amount),
                                      DBookEntry(entry_account, entry2_type, amount)])
                self._data.append(trans)
            else:
                yield from self._data

        
