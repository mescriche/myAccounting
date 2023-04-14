__author__ = 'Manuel Escriche'
from tkinter import *
from tkinter import ttk, messagebox
from tkinter.simpledialog import Dialog
from datetime import datetime, date
from dataclasses import dataclass
from datetime import datetime
from dbase import db_session, Account, Transaction, Type, BookEntry, db_currency, db_get_accounts_gname
import re, enum

@dataclass
class DMBookEntry:
    account : str
    type  : Type
    amount : float
    
@dataclass
class DMTransaction:
    id: int
    date: datetime.date
    description: str
    entries: list[DMBookEntry]

    @classmethod
    def from_DBTransaction(cls, trans):
        entries = [DMBookEntry(entry.account.gname, entry.type, entry.amount) for entry in trans.entries]
        return cls(trans.id, trans.date, trans.description, entries)

def DMBookEntry_dict(data):
    def get_name(obj):
        if isinstance(obj, enum.Enum):
            return obj.name
        return obj
    return dict((k, get_name(v)) for k, v in data)

def from_DBTrans_to_DMTrans(trans:Transaction) -> DMTransaction:
    entries = [DMBookEntry(entry.account.gname, entry.type, entry.amount) for entry in trans.entries]
    for entry in entries: print(entry)
    return DMTransaction(trans.id, trans.date, trans.description, entries)
    
class TransactionViewer(ttk.Frame):
    def __init__(self, parent, trans:DMTransaction, **kwargs):
        super().__init__(parent, **kwargs)
        self.pack(expand=False)
        Label(self, text=f'Transaction #{trans.id}', background='dark cyan').pack(fill='x')
        self.text= Text(self, height=3)
        self.text.pack(fill='x')
        self.text.insert(1.0, f'Date: {trans.date}\n')
        self.text.insert(2.0, f'Description: {trans.description}')
        self.text['state']='disabled'
        columns = ('debit', 'account', 'credit')
        data = dict()
        data['debit'] = {'text':'Debit', 'width':100, 'anchor':'e'}
        data['account'] = {'text':'Account', 'width':500, 'anchor':'w'}        
        data['credit'] = {'text':'Credit', 'width':100, 'anchor':'e'}
        
        self.table = ttk.Treeview(self, columns=columns, show='headings')
        self.table.pack()
        for topic in columns:
            self.table.heading(topic, text=data[topic]['text'])
            self.table.column(topic, width=data[topic]['width'], anchor=data[topic]['anchor'])
        else:
            self.table.tag_configure('total', background='lightblue')
        
        for entry in trans.entries:
            entry_debit = db_currency(entry.amount) if entry.type == Type.DEBIT else '-'
            entry_credit = db_currency(entry.amount) if entry.type == Type.CREDIT else '-'                
            values = entry_debit, entry.account, entry_credit
            self.table.insert('','end', values=values)
        else:
            trans_debit = sum([entry.amount for entry in trans.entries if entry.type == Type.DEBIT])
            trans_credit = sum([entry.amount for entry in trans.entries if entry.type == Type.CREDIT])
            self.table.insert('','end', values=(db_currency(trans_debit), '', db_currency(trans_credit)), tag='total')
            self.table.config(height=1+len(trans.entries))
        
class TransactionDialog(Dialog):
    def __init__(self, parent, title, trans:DMTransaction):
        self.trans = trans
        self.answer = False
        super().__init__(parent, title)

    def body(self, master):
        viewer = TransactionViewer(master, self.trans)
        return viewer 

    def buttonbox(self):
        control_bar = ttk.Frame(self)
        ttk.Label(control_bar, text='').pack(side='left', expand=True, fill='x')
        ttk.Button(control_bar, text="Cancel", width=10, command=self.cancel).pack(side='left', padx=5, pady=5)
        ttk.Label(control_bar, text='').pack(side='left', expand=True, fill='x')
        ttk.Button(control_bar, text="Record", width=10, command=self.ok, default=ACTIVE).pack(side='left', padx=5, pady=5)
        ttk.Label(control_bar, text='').pack(side='left', expand=True, fill='x')
        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.cancel)
        control_bar.pack(fill='x')
        
    def apply(self):
        self.answer = True

    def validate(self):
        return True

def transactionDialog(master, title, trans):
    w = TransactionDialog(master, title, trans)
    return w.answer

class TransactionUpdater(Dialog):
    def __init__(self, parent, title, trans:DMTransaction, **kwargs):
        self.trans = trans
        super().__init__(parent, title)

    def body(self, master):
        viewer = TransactionViewer(master, self.trans)
        return viewer 

    def buttonbox(self):
        control_bar = ttk.Frame(self)
        ttk.Label(control_bar, text='').pack(side='left', expand=True, fill='x')
        ttk.Button(control_bar, text="Cancel", width=10, command=self.cancel).pack(side='left', padx=5, pady=5)
        ttk.Label(control_bar, text='').pack(side='left', expand=True, fill='x')
        ttk.Button(control_bar, text="Update", width=10, command=self.ok, default=ACTIVE).pack(side='left', padx=5, pady=5)
        ttk.Label(control_bar, text='').pack(side='left', expand=True, fill='x')
        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.cancel)
        control_bar.pack(fill='x')

                
    def apply(self):
        self.answer = True

    def validate(self):
        return True


    
class TransactionEditor(Dialog):
    errormessage = 'Not a Transaction'
    
    def __init__(self, parent,  **kwargs):
        title = 'Transaction Editor'
        self.trans = None
        super().__init__(parent, title)
        
    def body(self, master):
        self.text= Text(master, height=3)
        self.text.pack(fill='x')
        
        columns = ('debit', 'account', 'credit')
        data = dict()
        data['debit'] = {'text':'Debit', 'width':100, 'anchor':'e'}
        data['account'] = {'text':'Account', 'width':500, 'anchor':'w'}        
        data['credit'] = {'text':'Credit', 'width':100, 'anchor':'e'}
        self.table = ttk.Treeview(master, columns=columns, show='headings')
        self.table.pack()
        for topic in columns:
            self.table.heading(topic, text=data[topic]['text'])
            self.table.column(topic, width=data[topic]['width'], anchor=data[topic]['anchor'])
        else:
            self.table.tag_configure('total', background='lightblue')
        self.table.bind('<Double-1>', self._edit_table)
        self.render()
        return self.table

    def render(self):
        date = '23-02-2022'
        description = 'Compra en Mercadona'
        self.text.insert(1.0, f'Date:{date}\n')
        self.text.insert(2.0, f'Description:{description}\n')
        for entry in range(4):
            self.table.insert('','end', values=('','',''))
        else:
            self.table.insert('','end', values=('','',''), tag='total')
            nrows = len([iid for iid in self.table.get_children()])
            self.table.config(height=nrows)
            
    def buttonbox(self):
        control_bar = ttk.Frame(self)
        ttk.Label(control_bar, text='').pack(side='left', expand=True, fill='x')
        ttk.Button(control_bar, text="Cancel", width=10, command=self.cancel).pack(side='left', padx=5, pady=5)
        ttk.Label(control_bar, text='').pack(side='left', expand=True, fill='x')
        ttk.Button(control_bar, text="Save", width=10, command=self.ok, default=ACTIVE).pack(side='left', padx=5, pady=5)
        ttk.Label(control_bar, text='').pack(side='left', expand=True, fill='x')
        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.cancel)
        control_bar.pack(fill='x')

    def validate(self):
        # validate date
        try:
            date = re.search(r'(?<=^Date:).+', self.text.get(1.0, '1.end')).group(0).strip()
            date = datetime.strptime(date, "%d-%m-%Y").date()
        except AttributeError:
            messagebox.showwarning( message = self.errormessage + "\nMissing date" + "\nPlease try again", parent = self )
            return False
        except ValueError:
            messagebox.showwarning( message = self.errormessage + "\nWrong date value or format" + "\nPlease try again", parent = self )
            return False
        except Exception as e:
            print(e)
            return False
        # validate description
        try:
            description = re.search(r'(?<=^Description:).+',self.text.get(2.0, 'end-1c')).group(0)
        except AttributeError:
            messagebox.showwarning( message = self.errormessage + "\nMissing Description" + "\nPlease try again", parent = self )
            return False        
        except Exception as e:
            print(e)
            return False
        # exclude empty entries
        #for iid in self.table.get_children():
        #    entry = self.table.item(iid,'values')
        #    if not self.table.tag_has('total', iid) and any(entry):
        #        print(iid, entry)

        non_empty_entries_iids = list(filter(lambda x: not self.table.tag_has('total', x) and any(self.table.item(x, 'values')), self.table.get_children()))        
        
        if len(non_empty_entries_iids) < 2:
            messagebox.showwarning(message=self.errormessage + f"\nAt least two book entries are required" + "\nPlease try again", parent=self)
            return False
        # validate entries
        total_debit, total_credit = 0,0
        for n,iid in enumerate(non_empty_entries_iids):
            if self.table.tag_has('total', iid): continue
            # validate account
            account = self.table.set(iid, column='account')
            if not account:
                messagebox.showwarning(message=self.errormessage +f"\nMissing account #{n+1}" + "\nPlease try again", parent=self)
                return False
            if not account in db_get_accounts_gname():
                messagebox.showwarning(message=self.errormessage +f"\nWrong account #{n+1}" + "\nPlease try again", parent=self)
                return False
            # validate amounts
            debit = self.table.set(iid, column='debit').replace('.','').replace(',','.')
            credit = self.table.set(iid, column='credit').replace('.','').replace(',','.')
            if not debit and not credit:
                messagebox.showwarning(message=self.errormessage +f"\nMissing amount in entry #{n+1}" + "\nPlease try again", parent=self)
                return False
            if debit:
                try: debit = float(debit)
                except ValueError:
                    messagebox.showwarning(message=self.errormessage +f"\nWrong amount in debit #{n+1}" + "\nPlease try again", parent=self)
                    return False
                except Exception as e:
                    print(e)
                    return False
                else:
                    if debit < 0:
                        messagebox.showwarning(message=self.errormessage + f"\nAmount in debit #{n+1} must be positive" + "\nPlease try again", parent=self)
                        return False                        
                    else:
                        total_debit += debit                
            if credit:
                try: credit = float(credit)
                except ValueError:
                    messagebox.showwarning(message=self.errormessage +f"\nWrong amount in credit #{n+1}" + "\nPlease try again", parent=self)
                    return False
                except Exception as e:
                    print(e)
                    return False
                else:
                    if credit < 0:
                        messagebox.showwarning(message=self.errormessage + f"\nAmount in credit #{n+1} must be positive" + "\nPlease try again", parent=self)
                        return False
                    else:
                        total_credit += credit
            if debit and credit:
                messagebox.showwarning(message=self.errormessage +f"\nOnly credit or debit amount is accepted in book entry#{n+1}" + "\nPlease try again", parent=self)
                return False
        else:
            # validate total
            if total_debit != total_credit:
                messagebox.showwarning(message=self.errormessage+f"total debit and credit amounts must match"+"\nPlease, try again", parent=self)
                return False
            else:
                return True
                    
    def apply(self):
        entries = list()
        non_empty_entries_iids = filter(lambda x: not self.table.tag_has('total', x) and any(self.table.item(x, 'values')), self.table.get_children())
        for iid in non_empty_entries_iids:
            account = self.table.set(iid, column='account')
            try: debit = float(self.table.set(iid, column='debit').replace('.','').replace(',','.'))
            except: debit = 0.0
            try: credit = float(self.table.set(iid, column='credit').replace('.','').replace(',','.'))
            except: credit = 0.0
            type = Type.DEBIT if debit > credit else Type.CREDIT
            amount = debit if type == Type.DEBIT else credit
            entries.append(DMBookEntry(account, type, amount))
        date = re.search(r'(?<=^Date:).+', self.text.get(1.0, '1.end')).group(0)
        description = re.search(r'(?<=^Description:).+',self.text.get(2.0, 'end-1c')).group(0)
        self.trans = DMTransaction(id=0, date=date, description=description, entries=entries)
        print(self.trans)

    def _edit_table(self, event):
        table = event.widget
        iid = table.focus()
        if table.tag_has('total', iid):
            self.table.delete(iid)
            self.table.insert('','end', values=('','',''))
            self.table.insert('','end', values=('','',''), tag='total')
            nrows = len([iid for iid in self.table.get_children()])
            self.table.config(height=nrows)
            return 'break'
        row = table.identify_row(event.y)
        column = table.identify_column(event.x)
        element = table.identify_element(event.x, event.y)
        region = table.identify_region(event.x, event.y)
       # print(f'iid={iid}, row={row}, column={column}, element={element}, region={region}')
        if element=='text' and region == 'cell':
            column_box = event.widget.bbox(row, column)
            if column in ('#1','#3'):
                field_edit = ttk.Entry(table, width=column_box[2])
                field_edit.place(x=column_box[0], y=column_box[1], w=column_box[2], h=column_box[3])
                field_edit.editing_item_iid = iid
                field_edit.editing_column = int(column[1])-1
                field_edit.focus()
                field_edit.bind('<FocusOut>', self._on_focus_out)
                field_edit.bind('<Return>', self._on_field_return)
            elif column == '#2':
                account_edit = ttk.Combobox(table, state='readonly', width=column_box[2])
                account_edit.config(values=db_get_accounts_gname())
                account_edit.place(x=column_box[0], y=column_box[1], w=column_box[2], h=column_box[3])        
                account_edit.editing_item_iid = iid
                account_edit.editing_column = int(column[1])-1
                account_edit.focus()
                account_edit.bind('<FocusOut>', self._on_focus_out)
                account_edit.bind('<<ComboboxSelected>>', self._on_account_selected)
            else: pass
        return 'break'
    
    def _on_account_selected(self, event):
        field = event.widget
        new_value = field.get()
        iid = field.editing_item_iid
        column = field.editing_column
        self.table.set(iid, column=column, value=new_value)
        field.destroy()
        return 'break'
    
    def _on_field_return(self, event):
        field = event.widget
        new_value = field.get()
        iid = field.editing_item_iid
        column = field.editing_column
        self.table.set(iid, column=column, value=new_value)
        field.destroy()
        debit, credit = 0,0
        for iid in self.table.get_children():
            if self.table.tag_has('total', iid):
                total_iid = iid
                continue
            try: debit += float(self.table.set(iid, column='debit').replace('.','').replace(',','.'))
            except: pass
            try: credit += float(self.table.set(iid, column='credit').replace('.','').replace(',','.'))
            except: pass
        else:
            self.table.set(total_iid, column='debit', value=debit)
            self.table.set(total_iid, column='credit', value=credit)
            if debit != credit:
                self.table.tag_configure('total', background='darksalmon')
            else:
                self.table.tag_configure('total', background='lightblue')
        return 'break'
    
    def _on_focus_out(self, event):
        event.widget.destroy()
        return 'break'
    
    
class NewTransactionEditor(Toplevel):
    def __init__(self, parent, trans:DMTransaction, **kwargs):
        super().__init__(parent, **kwargs)
        self.parent = parent
        self.trans_id = trans.id
        self.title('Transaction Editor')
        self.geometry('+{}+{}'.format(self._root().winfo_x()+44, self._root().winfo_y()+88))
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.viewer = TransactionViewer(self, trans)
        control_bar = ttk.Frame(self)
        control_bar.pack(fill='x')
        ttk.Label(control_bar, text='').pack(side='left', expand=True, fill='x')
        ttk.Button(control_bar, text='Cancel', command=self.dismiss).pack(side='left')
        ttk.Label(control_bar, text='').pack(side='left', expand=True, fill='x')
        ttk.Button(control_bar, text='Save', command=self.update_transaction).pack(side='left')
        ttk.Label(control_bar, text='').pack(side='left', expand=True, fill='x')
        self.viewer.text.bind('<Double-1>', self._edit_text)
        self.viewer.text.bind('<FocusOut>', self._on_text_focus_out)
        self.viewer.table.bind('<Double-1>', self._edit_table)
        #self.viewer.table.bind('<FocusOut>', self._on_focus_out)
        
        self.protocol("WM_DELETE_WINDOW", self.dismiss) # intercept close button
        self.wait_visibility() # can't grab until window appears, so we wait
        self.grab_set()        # ensure all input goes to our window
        self.wait_window()     # block until window is destroyed
        
    def _edit_text(self, event):
        self.viewer.text['state']='normal'
        return 'break'
    
    def _on_text_focus_out(self, event):
        if event.widget == self.viewer.text:
            self.viewer.text['state'] = 'disabled'
        return 'break'
    
    def _edit_table(self, event):
        table = event.widget
        iid = table.focus()
        if table.tag_has('total', iid):
            return 'break'
        row = table.identify_row(event.y)
        column = table.identify_column(event.x)
        element = table.identify_element(event.x, event.y)
        region = table.identify_region(event.x, event.y)
       # print(f'iid={iid}, row={row}, column={column}, element={element}, region={region}')
        if element=='text' and region == 'cell':
            column_box = event.widget.bbox(row, column)
            if column in ('#1','#3'):
                field_edit = ttk.Entry(self.viewer.table, width=column_box[2])
                field_edit.place(x=column_box[0], y=column_box[1], w=column_box[2], h=column_box[3])
                field_edit.editing_item_iid = iid
                field_edit.editing_column = int(column[1])-1
                field_edit.focus()
                field_edit.bind('<FocusOut>', self._on_focus_out)
                field_edit.bind('<Return>', self._on_field_return)
            elif column == '#2':
                account_edit = ttk.Combobox(self.viewer.table, state='readonly', width=column_box[2])
                account_edit.config(values=db_get_accounts_gname())
                account_edit.place(x=column_box[0], y=column_box[1], w=column_box[2], h=column_box[3])        
                account_edit.editing_item_iid = iid
                account_edit.editing_column = int(column[1])-1
                account_edit.focus()
                account_edit.bind('<FocusOut>', self._on_focus_out)
                account_edit.bind('<<ComboboxSelected>>', self._on_account_selected)
            else: pass
        return 'break'
    def _on_account_selected(self, event):
        field = event.widget
        new_value = field.get()
        iid = field.editing_item_iid
        column = field.editing_column
        self.viewer.table.set(iid, column=column, value=new_value)
        field.destroy()
        return 'break'
    
    def _on_field_return(self, event):
        field = event.widget
        new_value = field.get()
        iid = field.editing_item_iid
        column = field.editing_column
        self.viewer.table.set(iid, column=column, value=new_value)
        field.destroy()
        debit, credit = 0,0
        for iid in self.viewer.table.get_children():
            if self.viewer.table.tag_has('total', iid):
                total_iid = iid
                continue
            try: debit += abs(float(self.viewer.table.set(iid, column='debit').replace('.','').replace(',','.')))
            except: pass
            try: credit += abs(float(self.viewer.table.set(iid, column='credit').replace('.','').replace(',','.')))
            except: pass
        else:
            self.viewer.table.set(total_iid, column='debit', value=debit)
            self.viewer.table.set(total_iid, column='credit', value=credit)
            if debit != credit:
                self.viewer.table.tag_configure('total', background='darksalmon')
            else:
                self.viewer.table.tag_configure('total', background='lightblue')
        return 'break'
    
    def _on_focus_out(self, event):
        event.widget.destroy()
        return 'break'
    
    def _collect_data(self):
        entries = list()
        for iid in self.viewer.table.get_children():
            account = self.viewer.table.set(iid, column='account')
            if not account: continue
            try: debit = abs(float(self.viewer.table.set(iid, column='debit').replace('.','').replace(',','.')))
            except: debit = 0.0
            try: credit = abs(float(self.viewer.table.set(iid, column='credit').replace('.','').replace(',','.')))
            except: credit = 0.0
            if debit == credit: raise Exception('Wrong data')
            type = Type.DEBIT if debit > credit else Type.CREDIT
            amount = debit if type == Type.DEBIT else credit
            entries.append(DMBookEntry(account,type,amount))
        date = re.search(r'(?<=^Date:).+', self.viewer.text.get(1.0, '1.end')).group(0)
        description = re.search(r'(?<=^Description:).+',self.viewer.text.get(2.0, 'end-1c')).group(0)
        return DMTransaction(id=self.trans_id, date=date, description=description, entries=entries)

    def update_transaction(self):
        trans = self._collect_data()
        self.parent.update_transaction(trans)
        self.dismiss()
        
    def dismiss(self):
        self.grab_release()
        self.destroy()
        
#class TransactionEditor(Toplevel):
#    def __init__(self, parent):
#        super().__init__(parent)
#        self.parent = parent
#        self.title('Transaction')
#        #self.config(bg='skyblue')
#        self.rowconfigure(0, weight=1)
#        self.columnconfigure(0, weight=1)
#        self.geometry('+{}+{}'.format(self._root().winfo_x()+44, self._root().winfo_y()+88))
        #self.geometry('700x300+300+200')
        
#        self.date_entry = StringVar()
#        self.account_entry = StringVar()
#        self.amount_entry = StringVar()

#        frame = ttk.Frame(self)
#        date_frame = ttk.Frame(frame)
#        ttk.Label(date_frame, text='Date:').pack(side='left')
#        vdate_wrapper = (self.register(self.validate_date), '%P')
#        date_entry = ttk.Entry(date_frame, width=10, textvariable=self.date_entry,
#                  validate='focusout', validatecommand=vdate_wrapper)
#        date_entry.pack(side='right')
#        date_frame.pack(padx=10, pady=10, ipadx=5, ipady=5)

#        ttk.Separator(frame, orient='horizontal').pack(fill='x', expand=True)
        
#        accounts_frame=ttk.Frame(frame)
#        columns = ('account', 'debit', 'credit')
#        self.data = ttk.Treeview(accounts_frame, height=5,
#                                       selectmode='browse', columns = columns, show='headings')
#        self.data.heading('debit', text='Debit(€)')
#        self.data.column('debit', width=100, stretch=False, anchor='e')        
#        self.data.heading('account' , text='Account')
#        self.data.column('account', width=200, stretch=True, anchor='w')
#        self.data.heading('credit', text='Credit(€)')
#        self.data.column('credit', width=100, stretch=False, anchor='e')
#        self.data.pack(fill='both',expand=True)
#        self.data.tag_configure('to', background='lightblue')
        

#        accounts_frame.pack(fill='both', expand=True)
        

#        plus_icon = PhotoImage(file='./view/icons/add.gif')  
#        minus_icon = PhotoImage(file='./view/icons/remove.gif')
#
#        controls_frame = ttk.Frame(frame)
#        controls_frame.pack(fill='x', expand=True)
#
#        leftside_buttons_frame = ttk.Frame(controls_frame)
#        Button(leftside_buttons_frame, image=minus_icon, command=self.remove_selected,
#               padx=0, pady=0, bd=0).pack(side='left', padx=2)
#        Button(leftside_buttons_frame, text='To', command=self.upload_to,
#               padx=0, pady=3, bd=0).pack(side='left', padx=2)
#        
#        input_frame = ttk.Frame(controls_frame)
#        #
#        input_acc_frame = ttk.Frame(input_frame)
#        ttk.Label(input_acc_frame, text="Account:").pack()
#        account_field = ttk.Combobox(input_acc_frame, state='readonly',
#                                     justify='center',
#                                     textvariable=self.account_entry)
#        account_field.bind('<<ComboboxSelected>>', lambda x:self.amount_entry.set(' '))
#        account_field.pack(anchor='center')
#        with db_session() as db:
#            account_field['values'] = [account.gname for account in db.query(Account).all()]
#        account_field.current(0)
#        input_acc_frame.pack( side='left', fill='x', expand=True)
        #
#        input_amnt_frame=ttk.Frame(input_frame)
#        ttk.Label(input_amnt_frame, text="Amount(€):").pack()
#        vamount_wrapper = (self.register(self.validate_amount), '%P')
#        ttk.Entry(input_amnt_frame, width=12, justify='right',
#                  textvariable=self.amount_entry,
#                  validate='key', validatecommand=vamount_wrapper).pack()
#        input_amnt_frame.pack(side='left', fill='x', expand=True)
#
#        rightside_buttons_frame = ttk.Frame(controls_frame)
#        Button(rightside_buttons_frame, text='Debit', command=self.upload_debit,
#               padx=0, pady=3, bd=0).pack(side='left', padx=2)
#        Button(rightside_buttons_frame, text='Credit', command=self.upload_credit,
#               padx=0, pady=3, bd=0).pack(side='left', padx=2)

#        leftside_buttons_frame.pack(side='left', anchor='s')
#        input_frame.pack(side='left', expand=True)
#        rightside_buttons_frame.pack(side='left', anchor='s')
#
#        ttk.Separator(frame, orient='horizontal').pack(fill='x', expand=True)
#        
#        text_frame = ttk.Labelframe(frame, text='Description:')
#        self.text = Text(text_frame, height=5)
#        self.text.config(bg='white', fg='black')
#        self.text.pack(fill='x', expand=True)
#        text_frame.pack(fill='x', expand=True)
#        
#        ttk.Separator(frame, orient='horizontal').pack(fill='x', expand=True)
        
#        buttons_frame=ttk.Frame(frame)
#        ttk.Button(buttons_frame, text='Dismiss', command=self.dismiss).pack(side='left', padx=10, pady=10)

#        self.verify_button = ttk.Button(buttons_frame, text="Verify", command=self.verify)
#        self.verify_button.pack(side='left', padx=10, pady=10)
#        
#        ttk.Button(buttons_frame, text="Save", command=self.save).pack(side='right', padx=10, pady=10)
#        buttons_frame.pack(side='bottom')
#        
#        frame.pack(side='top', anchor='n', fill='x', expand=True)
#        date_entry.focus()
#
#        self.date_entry.set('23-03-2022')
#        self.data.insert('','end', values=('[DR-51] Bank Account', '100', '0'))
#        self.data.insert('','end', values=('[CN-70] Income-Parents', '0', '100'))
#        self.text.insert(1.0, 'apoyo mensual')
#            
#        self.protocol("WM_DELETE_WINDOW", self.dismiss) # intercept close button
#        self.wait_visibility() # can't grab until window appears, so we wait
#        self.grab_set()        # ensure all input goes to our window
#        self.wait_window()     # block until window is destroyed

#    def validate_date(self, in_date) -> bool:
#        if not in_date: return True
#        else:
#            try:
#                datetime.strptime(in_date, "%d-%m-%Y")
#            except ValueError:
#                return False
#            else:
#                return True
                
#    def validate_amount(self, amnt) -> bool:
#        if not amnt: return True
#        else:
#            try: float(amnt)
#            except ValueError:
#                return False
#            return True
        
#    def upload_debit(self):
#        if not self.amount_entry.get(): return
#        try: amount = float(self.amount_entry.get())
#        except ValueError: pass
#        else:
#            self.data.insert('','end', values=(self.account_entry.get(), amount, '-'))
#        finally:
#            self.amount_entry.set(' ')

#    def upload_credit(self):
#        if not self.amount_entry.get(): return
#        try: amount = float(self.amount_entry.get())
#        except: ValueError
#        else:
#            self.data.insert('','end', values=(self.account_entry.get(), '-', amount))
#        finally:
#            self.amount_entry.set(' ')
#    def upload_to(self):
#        self.data.insert('', 'end', values=('{:-^70}'.format(' To '), '', ''), tags=('to'))
#            
#    def remove_selected(self):
#        try: item = self.data.selection()[0]
#        except IndexError: pass
#        else: self.data.delete(item)
#            
#    def dismiss(self):
#        self.grab_release()
#        self.destroy()
#
#    def save(self):
#        try: self.verify_input()
#        except Exception as error:
#            title = "Verifiying transaction"
#            messagebox.showerror(title=title, message=error.message)
#        else:
#            ptrn = re.compile(r'\[((C|D)(R|N))-(?P<code>\d+)\]\s[-\s\w]+')
#            with db_session() as db:
#                description =  self.text.get('1.0', 'end-1c')
#                try: date = datetime.strptime(self.date_entry.get(), '%d-%m-%Y').date()
#                except: raise Exception(f'Wrong date format:"{self.date_entry.get()}"')
#                transaction = Transaction(date=date, description=description)
#                db.add(transaction)
#                for child_id in self.data.get_children():
#                    child = self.data.item(child_id)
#                    acc_name, debit, credit = tuple(child['values'])
#                    if match := ptrn.fullmatch(acc_name):
#                        code = match.group('code')
#                        try: account = db.query(Account).filter_by(code=code).one()
#                        except: raise Exception(f'Unknown code:"{code}"')
#                        try: debit = abs(float(debit))
#                        except ValueError: debit = 0.0
#                        try: credit = abs(float(credit))
#                        except ValueError: credit = 0.0
#                        if debit > 0:
#                            db.add(BookEntry(account=account, transaction=transaction, type='DEBIT', amount=debit))
#                        elif credit > 0:
#                            db.add(BookEntry(account=account, transaction=transaction, type='CREDIT', amount=debit))
#                        else: raise Exception(f'Wrong BookEntry format')
#                    else : raise Exception(f'Wrong account pattern:"{acc_name}"')
#            self.master.event_generate("<<DataBaseContentChanged>>")
#            self.dismiss()
#    
#    def verify_input(self):
#        debit_total, credit_total = 0,0
#        for idd in self.data.get_children():
            #print(self.data.item(idd))
#            debit = self.data.set(idd, column='debit')
#            credit = self.data.set(idd, column='credit')
#            try: debit = float(debit)
#            except ValueError: pass    
#            else: debit_total += debit
#            try: credit = float(credit)
#            except ValueError: pass
#            else:  credit_total += credit                
#        if not debit_total or not credit_total:
#            raise Exception('Missing input for accounts')
#        if debit_total != credit_total:
#            raise Exception('Totals mismatch')
#        if not self.date_entry.get():
#            raise Exception('No Date')
#        comment = self.text.get('1.0', 'end-1c')
#        if not comment:
#            raise Exception('No Comment')
        
#    def verify(self):
#        try: self.verify_input()
#        except Exception as error:
#            title = "Verifiying transaction"
#            messagebox.showerror(title=title, message=error.message)
#        else:
#            self.verify_button.config(text='OK')
#            self.after(2000, lambda: self.verify_button.config(text='Verify'))



#class DMTransactionEditor(TransactionEditor):
#    def __init__(self, parent):
#        super().__init__(parent)
#        
#    def save(self):
#        try: self.verify_input()
#        except Exception as error:
#            title = "Verifiying transaction"
#            messagebox.showerror(title=title, message=error.message)
#        else:
#            date = self.date_entry.get()
#            description = self.text.get(1.0, 'end-1c')
#            entries = list()
#            for cid in self.data.get_children():
#                #child = self.data.item(cid)
#                account = self.data.set(cid, column='account')
#                try: debit = float(self.data.set(cid, column='debit'))
#                except: debit = 0
#                try: credit = float(self.data.set(cid, column='credit'))
#                except: credit = 0
#                type = Type.DEBIT if debit > 0 else Type.CREDIT
#                amount = debit if type==Type.DEBIT else credit
#                entries.append(DMBookEntry(account,type, amount))
#            else:
#                trans = DMTransaction(0, date, description, entries)
#            self.parent.add_transaction(trans)
#            self.dismiss()
#        
#    def _save(self):
#        try: self.verify_input()
#        except ValidationError as error:
#            title = "Verifiying transaction"
#            messagebox.showerror(title=title, message=error.message)
#        else:
#            trans = dict()
#            trans['date'] = self.date_entry.get()
#            trans['description'] = self.text.get(1.0, 'end-1c')
#            trans['entries'] = list()
#            for child_id in self.data.get_children():
#                child = self.data.item(child_id)
#                acc_name, debit, credit = tuple(child['values'])
#                try: debit = abs(float(debit))
#                except ValueError: debit = 0.0
#                try: credit = abs(float(credit))
#                except ValueError: credit = 0.0
#                if debit > 0:
#                    trans['entries'].append({'account': acc_name, 'debit': debit })
#                elif credit > 0:
#                    trans['entries'].append({'account': acc_name, 'credit': credit })
#                else: raise Exception(f'Wrong BookEntry Format')
#            self.parent.add_transaction(trans)
#            self.dismiss()
