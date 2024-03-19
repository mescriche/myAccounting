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
import json, os, pickle
from datetime import datetime


class ExcelView(ttk.Frame):
    def __init__(self, parent, user_dir, **kwargs):
        super().__init__(parent, **kwargs)
        self.parent = parent
        self.pack(fill='both', expand=True)
        
        self.dirname = os.path.join(user_dir, 'excelfiles')
        self.filename = StringVar()
        
        file_bar = ttk.Labelframe(self, text='File')
        file_bar.pack(fill='x', ipady=4, ipadx=4)

        self.file_name_entry = ttk.Combobox(file_bar, textvariable=self.filename, width=40, postcommand= self._get_filenames)
        self.file_name_entry.pack(side='left', padx=5)
        self.file_name_entry.bind('<<ComboboxSelected>>', self._open_file)

        self.editor = None
        
    def _get_filenames(self):
        files = (file for file in os.listdir(self.dirname) if os.path.isfile(os.path.join(self.dirname, file)))
        _files = filter(lambda x: x.endswith('.xls') or x.endswith('.xlsx'), files)
        self.file_name_entry['values'] = sorted(list(_files), reverse=True)

    def _open_file(self, event=None):
        filename = os.path.join(self.dirname, self.filename.get())
        reader = create_excel_reader(filename)
        if os.path.basename(filename) == reader.filename:
            if self.editor: self.editor.destroy()
            self.editor = ExcelEditor(self, filename)
        else:
            #self.filename.set(reader.filename)
            new_filename = os.path.join(self.dirname, reader.filename)
            os.rename(filename, new_filename)

class ExcelEditor(ttk.Frame):
    #errormessage = 'Not a Transaction'
    def __init__(self, master, filename,  **kwargs):
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
        self.buttonbox()
        
        self.load(filename)
        
    def body(self):
        frame = ttk.Frame(self)
        frame.pack(expand=True, fill='x')

        filterframe = ttk.Labelframe(frame, text='Edit Filter')
        filterframe.pack(expand=False, side='left', fill='x')

        self.filter_account = StringVar()
        _labelframe = ttk.Labelframe(filterframe, text='Account')
        _labelframe.pack(side='left')
        account = ttk.Combobox(_labelframe, state='readonly', textvariable=self.filter_account, width=30)
        account.config(values= ['Any', 'None'] + db_get_accounts_gname())
        account.current(0)
        account.pack(side='left')
        
        self.filter_keyword = StringVar()
        _labelframe = ttk.Labelframe(filterframe, text='Description')
        _labelframe.pack(side='left', padx=10)
        self.keyword_wdgt = ttk.Combobox(_labelframe, textvariable=self.filter_keyword, width=50)
        #self.keyword_wdgt.bind('<<ComboboxSelected>>', self._set_filter_view)
        self.keyword_wdgt.pack(side='left')

        _frame = ttk.Frame(filterframe)
        filter_btn = ttk.Button(_frame, text='Filter', width=6, command=self._set_edit_filter)
        filter_btn.pack()
        clear_filter_btn = ttk.Button(_frame, text='Clear', width=6, command=self._clear_edit_filter)
        clear_filter_btn.pack()
        _frame.pack(side='left', padx=4)

        self.from_date = StringVar()
        self.to_date = StringVar()

        _dates_frame = ttk.Labelframe(frame, text='Time Filter')
        _datesentry_frame = ttk.Frame(_dates_frame)
        fromframe = ttk.Frame(_datesentry_frame)
        ttk.Label(fromframe, text='From:', width=5).pack(side='left')
        ttk.Entry(fromframe, textvariable=self.from_date, validate='focusout', validatecommand=self._check_from_date, width=10).pack()
        fromframe.pack(pady=5)

        toframe = ttk.Frame(_datesentry_frame)
        ttk.Label(toframe, text='To:', width=5).pack(side='left')
        ttk.Entry(toframe, textvariable=self.to_date, validate='focusout', validatecommand=self._check_to_date, width=10).pack()
        toframe.pack()
        _datesentry_frame.pack(side='left',padx=4)
        
        _frame = ttk.Frame(_dates_frame)
        filter_btn = ttk.Button(_frame, text='Filter', width=6, command=self._set_time_filter)
        filter_btn.pack()
        clear_filter_btn = ttk.Button(_frame, text='Clear', width=6, command=self._clear_time_filter)
        clear_filter_btn.pack()
        _frame.pack(padx=4)
        _dates_frame.pack(expand=True, side='left', fill='both')
        
        self.table = ttk.Treeview(self)
        self.table.pack(expand=True, fill='x')
        self.table.config(selectmode='extended')
        self.table.config(show='headings')
        columns = ('account', 'date','amount','description')
        self.table.config(columns=columns)
        self.table.config(displaycolumns=columns)
        self.table.heading('account', text='Account',
                           command=lambda: self._sort_column('account'))
        self.table.heading('date', text='Date', command=lambda: self._sort_column('date'))
        self.table.heading('amount', text='Amount(€)', command=lambda: self._sort_column('amount'))
        self.table.heading('description', text='Description', command=lambda: self._sort_column('description'))
        self.table.column('account', width=200, anchor='w')
        self.table.column('date', width=90, anchor='c')
        self.table.column('amount', width=80, anchor='e')
        self.table.column('description', width=850, anchor='w')
        #self.table.bind('<<TreeviewSelect>>', self._account_edit)
        #self.table.bind('<Button-1>', self._on_single_click)
        self.table.bind('<Double-1>', self._on_double_click)
        self.table.tag_configure('error', background='lightsalmon')
        self.table.tag_configure('ok', background='lime green')
        self.table.config(height=17)
        
        if self.table.tk.call('tk', 'windowingsystem') == 'aqua':
            self.table.bind('<2>', self._show_popup_menu)
            self.table.bind('<Control-1>', self._show_popup_menu)
        else:
            self.table.bind('<3>', self._show_popup_menu)
        return self.table

    def _sort_column(self, col, reverse=False):
        #_id = self.table.column(col, option='id')
        if col in ('account', 'description'): key = lambda x: str(x[0])
        elif col == 'date':   key = lambda x:  datetime.strptime(x[0], "%d-%m-%Y").date()
        elif col == 'amount': key = lambda x: float(x[0])
        else: return
        
        l = [(self.table.set(iid, col), iid) for iid in self.table.get_children()]
        l.sort(key=key, reverse=reverse)
        for ndx, (val, iid) in enumerate(l):
            self.table.move(iid, '', ndx)
        else:
            self.table.heading(col, command=lambda: self._sort_column(col, not reverse))
            
    def _show_popup_menu(self, event):
        menu = Menu(self.table)
        menu.add_command(label='Assign account', command=lambda:self._show_accounts_list(event))
        menu.add_command(label='Clear account', command=lambda:self._clean_selection(event))
        menu.post(event.x_root, event.y_root)        
           
    def buttonbox(self):
        control_bar = ttk.Frame(self)
        ttk.Label(control_bar, text='').pack(side='left', expand=True, fill='x')
        save_file_icon = PhotoImage(file='./view/icons/save_file.gif')
        save_file_btn = ttk.Button(control_bar, compound=LEFT, image=save_file_icon, text="Save", width=10, command=self.save)
        save_file_btn.image = save_file_icon
        save_file_btn.pack(side='left', padx=5, pady=5)
        
        ttk.Label(control_bar, text='').pack(side='left', expand=True, fill='x')
        ttk.Button(control_bar, text="Validate", width=10, command=self.verify).pack(side='left', padx=5, pady=5)
        ttk.Label(control_bar, text='').pack(side='left', expand=True, fill='x')
        ttk.Button(control_bar, text="to Blackboard", width=10, command=self.to_blackboard).pack(side='left', padx=5, pady=5)
        ttk.Label(control_bar, text='').pack(side='left', expand=True, fill='x')
        control_bar.pack(expand=True, fill='x')

    def _check_from_date(self):
        try: _date_in = datetime.strptime(self.from_date.get(), "%d-%m-%Y").date()
        except:
            self.bell()
            self.from_date.set(self._from_date.strftime("%d-%m-%Y"))
            return False
        else:
            _from_date, _to_date = self._get_time_frame()
            if _from_date <= _date_in <= _to_date: return True
            else: 
                self.from_date.set(self._from_date.strftime("%d-%m-%Y"))
                self.bell()
                return False
            
    def _check_to_date(self):
        try:
            _date_in = datetime.strptime(self.to_date.get(), "%d-%m-%Y").date()
        except:
            self.bell()
            self.to_date.set(self._to_date.strftime("%d-%m-%Y"))
            return False
        else:
            _from_date, _to_date = self._get_time_frame()
            if _from_date <= _date_in <= _to_date: return True
            else: 
                self.to_date.set(self._to_date.strftime("%d-%m-%Y"))
                self.bell()
                return False
    
    def load(self, filename):
        reader = create_excel_reader(filename)
        self.entity.set(f'Entity: {reader.entity}')
        self.owner.set(f'Owner: {reader.owner}')
        self.description.set(f'Description: {reader.description}')
        self.file_account.set(f'CCC: {reader.account}')
        self.download.set(f'Downloaded on: {reader.downloaded_on}')
        self._filename.set(f'Filename: {reader.filename}')
        
        basename, ext = os.path.splitext(filename)
        restore_filename = basename + '.pickle'
        self.filename = filename

        self.table.delete(*self.table.get_children())

        with db_session() as db:
            for account in db.query(Account):
                if account.parameters and 'CCC' in account.parameters:
                    _account = account.parameters['CCC'].replace(' ','')       
                    if reader.account == _account:
                        self.master_account_id = account.id
                        acc_name = account.gname
                        break
            else: acc_name = 'Not found'
            
            self.account.set(f'Account: {acc_name}')
            
        if os.path.isfile(restore_filename):
            with open(restore_filename, 'rb') as f:
                data, self._entry_iids, _from_date, _to_date = pickle.load(f)
            for entry in data:
                self.table.insert('', 'end', values=entry)
            self.from_date.set(_from_date)
            self.to_date.set(_to_date)
            self._set_time_filter()
            
        else: 
            total = 0
            for n,item in enumerate(reader.data):
                values = '', item['vdate'].strftime("%d-%m-%Y"), item['amount'], item['comment']
                self.table.insert('', 'end', values=values)
                total += item['amount']
            else:
                self._entry_iids = [iid for iid in self.table.get_children()]
                self._clear_time_filter()
                
    @property
    def all_iids(self):
        return self._entry_iids
        
    def _get_time_frame(self):
        _from_date = min(map(lambda iid: datetime.strptime(self.table.set(iid, column='date'), "%d-%m-%Y").date(), self.all_iids))
        _to_date = max(map(lambda iid: datetime.strptime(self.table.set(iid, column='date'), "%d-%m-%Y").date(), self.all_iids))
        return (_from_date, _to_date)
        
    def save(self, show_msgbox=True):
        basename, ext = os.path.splitext(self.filename)
        filename = basename + '.pickle'

        data = [self.table.item(iid)['values'] for iid in self.all_iids]
        _status_data = (data, self._entry_iids, self.from_date.get(), self.to_date.get())
        
        with open(filename, 'wb') as f:
            # Pickle the 'data' dictionary using the highest protocol available.
            pickle.dump(_status_data, f, pickle.HIGHEST_PROTOCOL)
        if show_msgbox:
            messagebox.showwarning(message=f'Sheet status saved on file', parent=self)
            
    def verify(self):
        #check entries with account column assigned, others are ignored
        for n,iid in enumerate(self.all_iids):
            self.table.item(iid, tags = ('ok'))
            self.table.see(iid)
            account = self.table.set(iid, column='account')
            if not account:
                self.table.item(iid, tag='error')
                continue
            if account not in db_get_accounts_gname():
                self.table.item(iid, tag='error')
                continue
            date = self.table.set(iid, column='date')
            if not date:
                self.table.item(iid, tag='error')
                continue
            try: date = datetime.strptime(date, "%d-%m-%Y").date()
            except ValueError:
                self.table.item(iid, tag='error')
                continue
            amount = self.table.set(iid, column='amount')
            if not amount:
                self.table.item(iid, tag='error')
                continue
            try: float(amount)
            except ValueError:
                self.table.item(iid, tag='error')
                continue
            description = self.table.set(iid, column='description')
            if not description:
                self.table.item(iid, tag='error')
                continue
    def to_blackboard(self):
        self.verify()
        self.apply()
        notebook = self.master.master # notebook
        blackboard = self.master.master.master.output #blackboard
        blackboard.editor.clear()
        blackboard.editor.add_new_transaction(self.trans_list)
        blackboard.set_filename(self.filename)
        notebook.select(3) #blackboard
        
    def apply(self):
        self.save(show_msgbox=False)
        data = list()
        with db_session() as db:
            master_account = db.query(Account).get(self.master_account_id)
            for n, iid in enumerate(self.table.get_children()):
                if not self.table.tag_has('ok', iid): continue
                account, date, amount, description = self.table.item(iid)['values']
                date = datetime.strptime(date, "%d-%m-%Y").date()
                amount = float(amount)
                if master_account.type == Type.DEBIT:
                    entry1_type = Type.DEBIT if amount > 0 else Type.CREDIT
                elif master_account.type == Type.CREDIT:
                    entry1_type = Type.CREDIT if amount > 0 else Type.DEBIT
                else: raise Exception('Unknown entry type')
                entry2_type = Type.CREDIT if entry1_type == Type.DEBIT else Type.DEBIT
                amount = abs(amount)
                data.append(DMTransaction(id=n, date=date, description=description,
                                          entries = [DMBookEntry(master_account.gname, entry1_type, amount),
                                                     DMBookEntry(account, entry2_type, amount)]))
            else:
                self.trans_list = data

    def _clean_selection(self, event):
        if items := self.table.selection():
            for iid in items:
                self.table.set(iid, column='account', value='')
            else:
                self.table.selection_remove(items)

    def _show_accounts_list(self, event):
        if items := self.table.selection():
            iid = items[0]
            self.table.see(iid)
            column_box = self.table.bbox(iid, "2")
            items = StringVar(value= db_get_accounts_gname())
            account_list = Listbox(self.table, listvariable=items, selectmode='browse', width=40)
            account_list.place(x=column_box[0], y=column_box[1])
            account_list.bind('<<ListboxSelect>>', self._assign_selection)
            account_list.bind('<FocusOut>', lambda x: account_list.destroy())
            account_list.bind('<Escape>', lambda x: account_list.destroy())
            account_list.focus_set()
            
    def _assign_selection(self, event):
        items = self.table.selection()
        ndx = event.widget.curselection()
        new_value = event.widget.get(ndx)
        for iid in items:
            self.table.set(iid, column='account', value=new_value)
        else:
            self.table.selection_remove(items)
        event.widget.destroy()
        return 'break'
    
    def _on_single_click(self, event=None):
        print(event)
        region = self.table.identify_region(event.x, event.y)
        print(region)
        if region == 'heading':
            column = self.table.identify_column(event.x)
            print(column)
        #return 'break'
        
    def _on_double_click(self, event=None):
        iid = event.widget.focus()
        region = self.table.identify_region(event.x, event.y)
        if region == 'cell':
            description = self.table.set(iid, column='description')
            self.filter_keyword.set(description)
        return 'break'
    
    def _set_time_filter(self, event=None):
        try:
            _from_date = datetime.strptime(self.from_date.get(), "%d-%m-%Y").date()
            _to_date = datetime.strptime(self.to_date.get(), "%d-%m-%Y").date()            
        except Exception as err:
            print('Exception:', err)
            return
        for iid in self.all_iids:
            item_date = datetime.strptime(self.table.set(iid, column='date'), "%d-%m-%Y").date()
            if _from_date <= item_date <= _to_date:
                self.table.move(iid, '', 0) #reattach
            else: self.table.detach(iid)
        
    def _clear_time_filter(self, event=None):
        _from_date, _to_date = self._get_time_frame()
        self.from_date.set(_from_date.strftime("%d-%m-%Y"))
        self.to_date.set(_to_date.strftime("%d-%m-%Y"))
        self._set_time_filter()                   
        
    def _set_edit_filter(self, event=None):
        keyword = self.filter_keyword.get()              
        if keyword not in self.keyword_wdgt['values']:
            add_on = (keyword,) if isinstance(self.keyword_wdgt['values'], tuple) else keyword
            self.keyword_wdgt['values'] += add_on

        _account = self.filter_account.get()
        account = '' if _account == 'None' else _account
        if account != 'Any':
            for iid in self.table.get_children():
                item_account = self.table.set(iid, column='account')
                if item_account != account: self.table.detach(iid)
        if keyword:
            for iid in self.table.get_children():
                item_comment = self.table.set(iid, column='description')
                if  keyword not in item_comment: self.table.detach(iid)
            
    def _clear_edit_filter(self, event=None):
        self.filter_keyword.set('')
        self.filter_account.set('')
        self._set_time_filter()
    

      
