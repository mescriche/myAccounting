__author__ = 'Manuel Escriche'
from tkinter import *
from tkinter import ttk, messagebox
#from tkinter.simpledialog import Dialog
#from .dialog import Dialog
from dbase import db_session, Type, Account
from controller.utility import db_get_accounts_gname, db_get_profile, db_currency
from controller.excel_reader import create_excel_reader
from dataclasses import asdict
from .transaction import DMBookEntry, DMTransaction, DMTransactionEncoder
import json, os, pickle, datetime



class ExcelView(ttk.Frame):
    def __init__(self, parent, user_dir, **kwargs):
        super().__init__(parent, **kwargs)
        self.pack(fill='both', expand=True)
        self.dirname = os.path.join(user_dir, 'excelfiles')
        self.filename = StringVar()
        
        file_bar = ttk.Labelframe(self, text='File')
        file_bar.pack(expand=True, fill='x', ipady=4, ipadx=3)

        save_file_icon = PhotoImage(file='./view/icons/save_file.gif')
        save_file_btn = ttk.Button(file_bar, image=save_file_icon, command=self.save_file)
        save_file_btn.image = save_file_icon
        save_file_btn.pack(side='left',padx=10)

        self.file_name_entry = ttk.Combobox(file_bar, textvariable=self.filename, width=40, postcommand= self._get_filenames)
        self.file_name_entry.pack(side='left')
        self.file_name_entry.bind('<<ComboboxSelected>>', self._open_file)

        verify_btn = ttk.Button(file_bar, text='Verify', command = self.verify_table)
        verify_btn.pack(side='left', padx=10)
        
        export_btn = ttk.Button(file_bar, text='Blackboard', command = self.export)
        export_btn.pack(side='left', padx=10)
        
        self.editor = ExcelEditor(self)
        
    def _get_filenames(self):
        files = (file for file in os.listdir(self.dirname) if os.path.isfile(os.path.join(self.dirname, file)))
        _files = filter(lambda x: x.endswith('.xls') or x.endswith('.xlsx'), files)
        self.file_name_entry['values'] = sorted(list(_files), reverse=True)

    def _open_file(self, event=None):
        filename = os.path.join(self.dirname, self.filename.get())
        self.editor.load(filename)

    def execute_step_by_step(self):
        pass

    def execute(self):
        pass

    def save_file(self):
        pass

    def verify_table(self):
        pass

    def export(self):
        pass

class ExcelEditor(ttk.Frame):
    #errormessage = 'Not a Transaction'
    def __init__(self, master, **kwargs):
        self.trans_list = None
        self.filename = None
        super().__init__(master, **kwargs)
        self.pack(fill='both', expand=True)
        
        frame = ttk.Labelframe(self, text='About File')
        frame.pack(expand=True, fill='x')

        self.owner= StringVar()
        ttk.Label(frame, textvariable=self.owner).grid(row=1, column=1,  padx=10, sticky='w')
        
        self.entity = StringVar()
        ttk.Label(frame, textvariable=self.entity).grid(row=1, column=2, padx=10, sticky='w')
        
        self.description = StringVar()
        ttk.Label(frame, textvariable=self.description).grid(row=1, column=3,  padx=10, sticky='w')

        self.file_account = StringVar()
        ttk.Label(frame, textvariable=self.file_account).grid(row=1, column=4,  padx=10, sticky='w')

        self._filename = StringVar()
        ttk.Label(frame, textvariable=self._filename).grid(row=2, column=1, columnspan=2, padx=10, sticky='w')
        
        self.download = StringVar()
        ttk.Label(frame, textvariable=self.download).grid(row=2, column=3,  padx=10, sticky='w')

        self.account = StringVar()
        ttk.Label(frame, textvariable=self.account).grid(row=2, column=4, padx=10, sticky='w')
        
        self.body()
        #self.buttonbox()
        
    def body(self):
        frame = ttk.Frame(self)
        frame.pack(fill='x')

        labelframe = ttk.Labelframe(frame, text='Filter')
        labelframe.pack(side='left', fill='x')

        self.filter_account = StringVar()
        _labelframe = ttk.Labelframe(labelframe, text='Account')
        _labelframe.pack(side='left')
        account = ttk.Combobox(_labelframe, state='readonly', textvariable=self.filter_account, width=30)
        account.config(values= ['Any', 'None'] + db_get_accounts_gname())
        account.current(0)
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

        
        self.table = ttk.Treeview(self)
        self.table.pack(expand=True, fill='both')
        self.table.config(selectmode='browse')
        self.table.config(show='headings')
        columns = ('account', 'date','amount','description')
        self.table.config(columns=columns)
        self.table.config(displaycolumns=columns)        
        self.table.heading('date', text='Date')
        self.table.heading('account', text='Account')
        self.table.heading('amount', text='Amount(€)')
        self.table.heading('description', text='Description')
        self.table.column('account', width=200, anchor='w')
        self.table.column('date', width=90, anchor='c')
        self.table.column('amount', width=80, anchor='e')
        self.table.column('description', width=850, anchor='w')
        self.table.bind('<<TreeviewSelect>>', self._account_edit)
        self.table.bind('<Double-1>', self._on_double_click)
        self.table.tag_configure('master_account', background='light sky blue')
        self.table.tag_configure('error', background='lightsalmon')
        self.table.tag_configure('ok', background='lime green')
        self.table.config(height=20)
        
        return self.table
    
    def load(self, filename):
        basename, ext = os.path.splitext(filename)
        restore_filename = basename + '.pickle'
        self.filename = filename

        self.table.delete(*self.table.get_children())

        reader = create_excel_reader(filename)
        self.entity.set(f'Entity: {reader.entity}')
        self.owner.set(f'Owner: {reader.owner}')
        self.description.set(f'Description: {reader.description}')
        self.file_account.set(f'CCC: {reader.account}')
        self.download.set(f'Downloaded on: {reader.downloaded_on}')
        self._filename.set(f'Filename: {reader.filename}')

        with db_session() as db:
            for account in db.query(Account):
                print(account)
                if account.parameters and 'CCC' in account.parameters:
                    _account = account.parameters['CCC'].replace(' ','')       
                    if reader.account == _account:
                        acc_name = account.gname
                        break
            else: acc_name = 'Not found'
            self.account.set(f'Account: {acc_name}')
            
        if os.path.isfile(restore_filename):
            with open(restore_filename, 'rb') as f:
                data = pickle.load(f)
            for entry in data:
                self.table.insert('', 'end', values=entry)                
        else: 
            total = 0
            for n,item in enumerate(reader.data):
                values = '', item['vdate'].strftime("%d-%m-%Y"), item['amount'], item['comment']
                self.table.insert('', 'end', values=values)
                total += item['amount']

        self.entry_iids = [iid for iid in self.table.get_children()]
        
    def buttonbox(self):
        control_bar = ttk.Frame(self)
        ttk.Label(control_bar, text='').pack(side='left', expand=True, fill='x')
        #ttk.Button(control_bar, text="Cancel", width=10, command=self.cancel).pack(side='left', padx=5, pady=5)
        #ttk.Label(control_bar, text='').pack(side='left', expand=True, fill='x')
        ttk.Button(control_bar, text="Save", width=10, command=self.save).pack(side='left', padx=5, pady=5)
        ttk.Label(control_bar, text='').pack(side='left', expand=True, fill='x')
        ttk.Button(control_bar, text="Validate", width=10, command=self.validate).pack(side='left', padx=5, pady=5)
        ttk.Label(control_bar, text='').pack(side='left', expand=True, fill='x')
        ttk.Button(control_bar, text="to Blackboard", width=10, command=self.ok, default=ACTIVE).pack(side='left', padx=5, pady=5)
        ttk.Label(control_bar, text='').pack(side='left', expand=True, fill='x')
        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.cancel)
        control_bar.pack(fill='x')

    def validate(self):
        #validate entries with account column assigned, others are ignored
        for n,iid in enumerate(self.entry_iids):
            if iid == self.master_account_iid: continue
            self.table.item(iid, tags = ('ok'))
            self.table.see(iid)
            account = self.table.set(iid, column='account')
            if not account:
                self.table.item(iid, tag='error')
                messagebox.showwarning(message= f'Missing account at row #{n+1}' + "\n Please, try again", parent=self)
                #return False
                continue

            if account not in db_get_accounts_gname():
                self.table.item(iid, tag='error')
                messagebox.showwarning(message=f"Unknown account at row #{n+1}" + "\n Please, try again", parent=self)
                #return False
                continue
            date = self.table.set(iid, column='date')
            if not date:
                self.table.item(iid, tag='error')
                messagebox.showwarning(message=f'Missing date at row #{n+1}' + "\n Please, try again", parent=self)
                #return False
                continue
            try: date = datetime.datetime.strptime(date, "%d-%m-%Y").date()
            except ValueError:
                self.table.item(iid, tag='error')
                messagebox.showwarning(message=f'Wrong date value or format at row #{n+1}' + "\n Please, try again", parent=self)
                #return False
                continue
            amount = self.table.set(iid, column='amount')
            if not amount:
                self.table.item(iid, tag='error')
                messagebox.showwarning(message=f'Missing amount at row #{n+1}' + "\n Please, try again", parent=self)
                #return False
                continue
            try: float(amount)
            except ValueError:
                self.table.item(iid, tag='error')
                messagebox.showwarning(mesage=f'Wrong amount or format at row #{n+1}' + "\n Please, try again", parent=self)
                #return False
                continue
            description = self.table.set(iid, column='description')
            if not description:
                self.table.item(iid, tag='error')
                messagebox.showwarning(message=f'Missing description at row #{n+1}' + "\n Please, try again", parent=self)
                #return False
                continue
        return True

    def apply(self):
        self.save(show_msgbox=False)
        data = list()
        master_account = self.table.set(self.master_account_iid, column='account')
        macc_type = master_account[1]
        for n,iid in enumerate(self.entry_iids):
            if iid == self.master_account_iid: continue
            if not self.table.tag_has('ok', iid): continue
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
        basename, ext = os.path.splitext(self.filename)
        filename = basename + '.pickle'

        data = [self.table.item(iid)['values'] for iid in self.entry_iids]
        with open(filename, 'wb') as f:
            # Pickle the 'data' dictionary using the highest protocol available.
            pickle.dump(data, f, pickle.HIGHEST_PROTOCOL)
        if show_msgbox:
            messagebox.showwarning(message=f'Sheet status saved on file', parent=self)

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
        if account != 'Any':
            for iid in self.table.get_children():
                item_account = self.table.set(iid, column='account')
                if item_account != account: self.table.detach(iid)
        if keyword:
            for iid in self.table.get_children():
                item_comment = self.table.set(iid, column='description')
                if  keyword not in item_comment: self.table.detach(iid)
            
    def _clear_filter_view(self):
        self.filter_keyword.set('')
        self.filter_account.set('')
        for iid in self.entry_iids:
            self.table.move(iid, '', 0) #reattach
    
    def _account_edit(self, event=None):
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

    def _on_double_click(self, event=None):
        iid = event.widget.focus()
        region = self.table.identify_region(event.x, event.y)
        if region == 'cell':
            description = self.table.set(iid, column='description')
            self.filter_keyword.set(description)
        return 'break'

    def ok(self, event=None):
        try:
            self.apply()
        finally:
            self.cancel()
            
    def cancel(self, event=None):
        pass

