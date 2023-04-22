__author__ = 'Manuel Escriche'
from tkinter import *
from tkinter import ttk, messagebox
from tkinter.simpledialog import Dialog
from datetime import datetime, date
from dataclasses import dataclass
from dbase import db_session, Account, Transaction, Type, BookEntry, db_currency, db_get_accounts_gname
import re, enum, datetime, json

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
    def from_json(cls, data):
        entries = [DMBookEntry(entry['account'], Type[entry['type']], entry['amount']) for entry in data['entries']]
        return cls(data['id'], datetime.datetime.strptime(data['date'], '%d-%m-%Y').date(), data['description'], entries)
    @classmethod
    def from_DBTransaction(cls, trans):
        entries = [DMBookEntry(entry.account.gname, entry.type, entry.amount) for entry in trans.entries]
        return cls(trans.id, trans.date, trans.description, entries)
    def validate(self) ->bool:
        if not self.date or not isinstance(self.date, datetime.date): return False
        if not self.description or not isinstance(self.description, str): return False
        if len(self.entries) < 2: return False
        for entry in self.entries:
            if not entry.account or not isinstance(entry.account, str) or entry.account not in db_get_accounts_gname(): return False
            if not entry.type or not isinstance(entry.type, Type): return False
            if not entry.amount or not isinstance(entry.amount, float) or entry.amount < 0: return False
        return True

class DMTransactionEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, DMTransaction):
            item = dict()
            item['id'] = obj.id
            item['date'] = obj.date.strftime('%d-%m-%Y')
            item['description'] = obj.description
            item['entries'] = [{'account':entry.account, 'type':entry.type.name, 'amount':entry.amount } for entry in obj.entries]
            return item
        return super().default(obj)    
    
class TransactionViewer(ttk.Frame):
    def __init__(self, parent, trans:DMTransaction, **kwargs):
        super().__init__(parent, **kwargs)
        self.parent = parent
        self.pack(expand=False)
        Label(self, text=f'Transaction #{trans.id}', background='dark cyan').pack(fill='x')
        self.text= Text(self, height=3)
        self.text.pack(fill='x')
        self.text.insert(1.0, f'Date: {trans.date.strftime("%d-%m-%Y")}\n')
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
            
        self.table.bind('<<TreeviewSelect>>', self._display_account)
        
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
            
    def _display_account(self, event=None):
        if iid := event.widget.focus():
            account_name = event.widget.set(iid, column='account')
            wdgt = self
            while ancestor := wdgt.master:
                wdgt = ancestor
                if str(ancestor) == '.!view': break
            ancestor.ledger.account.set(account_name)
            ancestor.ledger.render_filter()
            ancestor.notebook.select(2)

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

def askTransactionRecordDialog(master, trans):
    w = TransactionDialog(master, 'Confirm Transaction', trans)
    return w.answer

class TransactionEditor(Dialog):
    errormessage = 'Not a Transaction'
    
    def __init__(self, parent, trans:DMTransaction=None, **kwargs):
        title = 'Transaction Editor'
        self.trans = trans
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
        self.table.config(selectmode='browse')
        self.table.pack()
        for topic in columns:
            self.table.heading(topic, text=data[topic]['text'])
            self.table.column(topic, width=data[topic]['width'], anchor=data[topic]['anchor'])
        else:
            self.table.tag_configure('total', background='lightblue')
        self.table.bind('<Double-1>', self._edit_table)
        #self.table.bind('<Button-1>', self._edit_table)
        self.render()
        return self.table

    def render(self):
        if self.trans is not None:
            self.table.delete(*self.table.get_children())
            self.text.insert(1.0, f'Date: {self.trans.date.strftime("%d-%m-%Y")}\n')
            self.text.insert(2.0, f'Description:{self.trans.description}\n')
            total = {Type.DEBIT:0, Type.CREDIT:0}
            for entry in self.trans.entries:
                values = (db_currency(entry.amount),entry.account,0) if entry.type == Type.DEBIT else (0 ,entry.account,db_currency(entry.amount))
                self.table.insert('','end', values=values)
                total[entry.type] += entry.amount
            else:
                self.table.insert('','end', values = (db_currency(total[Type.DEBIT]),'', db_currency(total[Type.CREDIT])), tag='total')
                
        else:
            self.text.insert(1.0, f'Date: \n')
            self.text.insert(2.0, f'Description: \n')
            for entry in range(2):
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
        ttk.Button(control_bar, text="Accept", width=10, command=self.ok, default=ACTIVE).pack(side='left', padx=5, pady=5)
        ttk.Label(control_bar, text='').pack(side='left', expand=True, fill='x')
        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.cancel)
        control_bar.pack(fill='x')

    def validate(self):
        # validate date
        try:
            date = re.search(r'(?<=^Date:).+', self.text.get(1.0, '1.end')).group(0).strip()
            date = datetime.datetime.strptime(date, "%d-%m-%Y").date()
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
                messagebox.showwarning(message=self.errormessage +f"\nMissing amount in entry #{n+1}" + "\nPlease try again",
                                       parent=self)
                return False
            if debit:
                try: debit = float(debit)
                except ValueError:
                    messagebox.showwarning(message=self.errormessage +f"\nWrong amount in debit #{n+1}" + "\nPlease try again",
                                           parent=self)
                    return False
                except Exception as e:
                    print(e)
                    return False
                else:
                    if debit < 0:
                        messagebox.showwarning(message=self.errormessage + f"\nAmount in debit #{n+1} must be positive" + "\nPlease try again",
                                               parent=self)
                        return False                        
                    else:
                        total_debit += debit                
            if credit:
                try: credit = float(credit)
                except ValueError:
                    messagebox.showwarning(message=self.errormessage +f"\nWrong amount in credit #{n+1}" + "\nPlease try again",
                                           parent=self)
                    return False
                except Exception as e:
                    print(e)
                    return False
                else:
                    if credit < 0:
                        messagebox.showwarning(message=self.errormessage + f"\nAmount in credit #{n+1} must be positive" + "\nPlease try again",
                                               parent=self)
                        return False
                    else:
                        total_credit += credit
            if debit and credit:
                messagebox.showwarning(message=self.errormessage +f"\nOnly credit or debit amount is accepted in book entry#{n+1}" + "\nPlease try again",
                                       parent=self)
                return False
        else:
            # validate total
            if total_debit != total_credit:
                messagebox.showwarning(message=self.errormessage+f"total debit and credit amounts must match"+"\nPlease, try again",
                                       parent=self)
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
        date = re.search(r'(?<=^Date:).+', self.text.get(1.0, '1.end')).group(0).strip()
        date = datetime.datetime.strptime(date, "%d-%m-%Y").date()
        description = re.search(r'(?<=^Description:).+',self.text.get(2.0, 'end-1c')).group(0)
        _id = self.trans.id if self.trans else 0
        self.trans = DMTransaction(id=_id, date=date, description=description, entries=entries)

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
            self.table.set(total_iid, column='debit', value=db_currency(debit))
            self.table.set(total_iid, column='credit', value=db_currency(credit))
            if debit != credit: self.table.tag_configure('total', background='darksalmon')
            else: self.table.tag_configure('total', background='lightblue')
        return 'break'
    
    def _on_focus_out(self, event):
        event.widget.destroy()
        return 'break'
